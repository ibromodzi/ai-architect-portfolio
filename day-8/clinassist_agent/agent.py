from dotenv import load_dotenv
load_dotenv("clinassist_agent/.env")

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.genai import types
from typing import Optional

from .config import MODEL
from .tools import lookup_symptoms, record_confirmation, record_rejection
from .callbacks import (
    health_safety_guardrail,
    append_disclaimer,
    validate_symptom_query,
    require_human_confirmation,
)


def skip_if_confirmation(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """Skip TriageAgent if this turn is a confirm/reject response."""
    status = callback_context.state.get("confirmation_status", "")
    if "confirmed" in status or "rejected" in status:
        return types.Content(
            role="model",
            parts=[types.Part(text="")]
        )
    return None


confirmation_handler = LlmAgent(
    name="ConfirmationHandler",
    model=MODEL,
    description="Handles confirm or reject responses from the human reviewer.",
    instruction=(
        "Check the user's message. "
        "If it is 'confirm' or similar approval, call record_confirmation. "
        "If it is 'reject' or similar rejection, call record_rejection. "
        "If it is neither, do nothing and output exactly: PASS"
    ),
    tools=[record_confirmation, record_rejection],
    output_key="confirmation_status",
    include_contents="none",
)

# triage_agent = LlmAgent(
#     name="TriageAgent",
#     model=MODEL,
#     description="Gathers symptoms and prepares a triage draft for human review.",
#     instruction=(
#         "You are ClinAssist, a health information assistant. "
#         "Your role is to help users understand their symptoms and "
#         "find general health information. You do NOT diagnose conditions "
#         "or recommend specific medications.\n\n"
#         "When the user reports symptoms:\n"
#         "1. Acknowledge their symptoms with empathy.\n"
#         "2. Use the lookup_symptoms tool to retrieve general information.\n"
#         "3. Summarise the general information clearly.\n"
#         "4. Always recommend consulting a healthcare professional.\n\n"
#         "If the user's request is outside your scope, say so clearly."
#     ),
#     tools=[lookup_symptoms],
#     output_key="triage_draft",
#     before_agent_callback=skip_if_confirmation,     # skip on confirm turns
#     before_model_callback=health_safety_guardrail,
#     before_tool_callback=validate_symptom_query,
# )

# Update the instruction field of triage_agent in agent.py

triage_agent = LlmAgent(
    name="TriageAgent",
    model=MODEL,
    description=(
        "Gathers patient-reported symptoms, retrieves evidence-based "
        "health information from the knowledge base, and prepares a "
        "cited triage draft for human review."
    ),
    instruction=(
        "You are ClinAssist, a health information assistant. "
        "Your role is to help users understand their symptoms using "
        "evidence retrieved from a curated health knowledge base. "
        "You do NOT diagnose conditions or recommend medications.\n\n"
        "When the user reports symptoms:\n"
        "1. Acknowledge their symptoms with empathy.\n"
        "2. Use the lookup_symptoms tool to retrieve relevant evidence.\n"
        "3. Summarise ONLY the information present in the retrieved evidence. "
        "Do not add information from your own knowledge.\n"
        "4. Cite the source of each piece of information using the source name "
        "provided in the evidence (e.g. 'According to headache.txt...').\n"
        "5. Include the when_to_seek_care advisory from the tool result.\n"
        "6. Recommend consulting a qualified healthcare professional.\n\n"
        "If no evidence is retrieved, say clearly that no information "
        "was found and recommend professional consultation."
    ),
    tools=[lookup_symptoms],
    output_key="triage_draft",
    before_agent_callback=skip_if_confirmation,
    before_model_callback=health_safety_guardrail,
    before_tool_callback=validate_symptom_query,
)


response_agent = LlmAgent(
    name="ResponseAgent",
    model=MODEL,
    description="Surfaces the confirmed triage response after human approval.",
    instruction=(
        "The confirmed triage draft is: {triage_draft}\n\n"
        "Present this information clearly and compassionately. "
        "Do not add new medical information."
    ),
    before_agent_callback=require_human_confirmation,
    after_model_callback=append_disclaimer,
    include_contents="none",
)

root_agent = SequentialAgent(
    name="ClinAssistPipeline",
    description="ClinAssist v0.1: triage with HITL gate and safety guardrails.",
    sub_agents=[confirmation_handler, triage_agent, response_agent],
)
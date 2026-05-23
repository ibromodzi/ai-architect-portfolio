# clinassist_agent/callbacks.py
# All callbacks for ClinAssist v0.1.
# Official ADK callback docs: https://google.github.io/adk-docs/callbacks/
# Official safety docs: https://google.github.io/adk-docs/safety/

from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.tools.base_tool import BaseTool
from google.adk.tools.tool_context import ToolContext
from google.genai import types

from .config import BLOCKED_PHRASES, DISCLAIMER, SAFETY_REJECTION

# ---------------------------------------------------------------------------
# 1. INPUT GUARDRAIL (before_model_callback)
# Blocks prohibited requests before they reach the LLM.
# ---------------------------------------------------------------------------


def health_safety_guardrail(
    callback_context: CallbackContext,
    llm_request: LlmRequest,
) -> Optional[LlmResponse]:
    """Scans user input for prohibited phrases and blocks the LLM call if any

    are found. Returning LlmResponse skips the LLM entirely. Returning None
    allows normal execution.
    """
    user_text = ""
    if llm_request.contents:
        for content in llm_request.contents:
            if content.role == "user":
                for part in content.parts:
                    if hasattr(part, "text") and part.text:
                        user_text += part.text.lower()

    for phrase in BLOCKED_PHRASES:
        if phrase in user_text:
            print(f"[GUARDRAIL] Blocked: '{phrase}'")
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=SAFETY_REJECTION)],
                )
            )

    return None


# ---------------------------------------------------------------------------
# 2. OUTPUT DISCLAIMER (after_model_callback)
# Appends the mandatory medical disclaimer to every response.
# Cannot be bypassed by user prompt engineering.
# ---------------------------------------------------------------------------


def append_disclaimer(
    callback_context: CallbackContext,
    llm_response: LlmResponse,
) -> Optional[LlmResponse]:
    """Appends the mandatory medical disclaimer to every model response.

    Returning a modified LlmResponse replaces the original.
    """
    if llm_response.content and llm_response.content.parts:
        original = llm_response.content.parts[0].text or ""

        # Do not double-append if disclaimer already present
        if DISCLAIMER.strip() not in original:
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=original + DISCLAIMER)],
                )
            )

    return None


# ---------------------------------------------------------------------------
# 3. TOOL ARGUMENT VALIDATOR (before_tool_callback)
# Validates lookup_symptoms arguments before the tool executes.
# ---------------------------------------------------------------------------


def validate_symptom_query(
    tool: BaseTool,
    args: dict,
    tool_context: ToolContext,
) -> Optional[dict]:
    """Validates tool arguments before lookup_symptoms executes.

    Returning a dict blocks the tool and uses it as the result. Returning None
    allows the tool to execute normally.
    """
    if tool.name != "lookup_symptoms":
        return None  # Only validate this specific tool

    query = args.get("query", "").strip()
    if not query:
        return {
            "status": "error",
            "error_message": "Symptom query cannot be empty.",
        }

    crisis_terms = ["suicide", "self harm", "overdose how to", "end my life"]
    for term in crisis_terms:
        if term in query.lower():
            return {
                "status": "blocked",
                "error_message": (
                    "If you are experiencing a mental health crisis, please contact a crisis helpline immediately. "
                    "In Nigeria: Suicide Research and Prevention Initiative (SURPIN) --- 08111909909."
                ),
            }

    return None


# ---------------------------------------------------------------------------
# 4. HITL CONFIRMATION GATE (before_agent_callback)
# Blocks the response agent until human approval is recorded in state.
# ---------------------------------------------------------------------------


def require_human_confirmation(
    callback_context: CallbackContext,
) -> Optional[types.Content]:
    """Pauses the ResponseAgent until state['user:confirmed'] is True.

    Returning Content skips the agent and surfaces the draft for review.
    Returning None allows the agent to execute normally.

    To approve in adk web: send the message 'confirm'. The ConfirmationHandler
    agent (registered in the pipeline) listens for this and sets
    state['user:confirmed'] = True.
    """
    confirmed = callback_context.state.get("user:confirmed", False)

    # if not confirmed:
    #     draft = callback_context.state.get("triage_draft", "No draft available yet.")
    #     return types.Content(
    #         role="model",
    #         parts=[
    #             types.Part(
    #                 text=(
    #                     "A triage draft has been prepared and requires your confirmation before it is shown.\n\n"
    #                     f"Draft:\n{draft}\n\n"
    #                     "Reply 'confirm' to approve and see the full response, or 'reject' to discard it."
    #                 )
    #             )
    #         ],
    #     )

    # return None

    if not confirmed:
        draft = callback_context.state.get("triage_draft", "No draft available.")
        return types.Content(
            role="model",
            parts=[types.Part(
                text=(
                    "A triage draft has been prepared and requires your "
                    "confirmation before it is shown.\n\n"
                    f"Draft:\n{draft}\n\n"
                    "Reply 'confirm' to approve or 'reject' to discard."
                )
            )],
        )
    # Reset flag after releasing so next query starts fresh
    callback_context.state["user:confirmed"] = False
    return None
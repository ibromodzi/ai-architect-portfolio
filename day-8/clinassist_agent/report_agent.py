# clinassist_agent/report_agent.py
from google.adk.agents import LlmAgent
from .config import MODEL
from .schemas import ClinTriageReport

report_agent = LlmAgent(
    name="ReportAgent",
    model=MODEL,
    description=(
        "Converts a triage draft and retrieved evidence into a "
        "schema-validated structured JSON clinical report. Does not call any tools."
    ),
    instruction=(
        "You are a clinical report formatter. You will be given a triage draft containing "
        "retrieved evidence from an eye health knowledge base.\n\n"
        "Triage draft:\n{triage_draft}\n\n"
        "Using ONLY the information in the triage draft above, produce a structured report "
        "with the following fields:\n"
        "- symptom_summary: one to two sentences summarising the reported symptoms\n"
        "- retrieved_evidence: list of relevant passages from the draft (copy them directly)\n"
        "- sources: list of source file names mentioned in the draft (e.g. 'conjunctivitis.txt')\n"
        "- triage_recommendation: what the user should do next\n"
        "- urgency_level: exactly one of 'routine', 'low', 'medium', or 'urgent'\n"
        "- disclaimer: use the default value from the schema\n\n"
        "Do not add any information not present in the triage draft. Do not call any tools. "
        "Respond with the JSON object only."
    ),
    output_schema=ClinTriageReport,
    output_key="triage_report",
    include_contents="none",
)
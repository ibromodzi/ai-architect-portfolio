# clinassist_agent/schemas.py
from pydantic import BaseModel, Field
from typing import Literal

DISCLAIMER_TEXT = (
    "This report is for general educational information only and does "
    "not constitute medical advice. Always consult a qualified healthcare "
    "professional for diagnosis, treatment, or any health-related decisions."
)

class ClinTriageReport(BaseModel):
    symptom_summary: str = Field(
        description=(
            "A concise one-to-two sentence neutral summary of the "
            "symptoms reported by the user."
        )
    )
    retrieved_evidence: list[str] = Field(
        description=(
            "Relevant passages retrieved from the eye health knowledge base. "
            "Each entry must come from retrieved chunks, not model memory."
        )
    )
    sources: list[str] = Field(
        description=(
            "Source file names that the retrieved evidence came from. "
            "Must contain at least one entry."
        )
    )
    triage_recommendation: str = Field(
        description=(
            "Plain-language recommendation for what the user should do "
            "next, based only on the retrieved evidence."
        )
    )
    urgency_level: Literal["routine", "low", "medium", "urgent"] = Field(
        description=(
            "The evaluated prioritization level for medical assessment: "
            "'routine' = standard wellness monitoring; "
            "'low' = home care and self-monitoring; "
            "'medium' = seek care within 24-48 hours; "
            "'urgent' = seek same-day or emergency care immediately."
        )
    )
    disclaimer: str = Field(
        default=DISCLAIMER_TEXT,
        description="Mandatory medical liability disclaimer appended to all structural summaries."
    )
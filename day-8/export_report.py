# export_report.py
# Reads triage_report from session state and exports a
# formatted PDF.
# Run from day-8/ with: python export_report.py "your symptom query"

from dotenv import load_dotenv
load_dotenv("clinassist_agent/.env")

import asyncio , json , sys
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet , ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
SimpleDocTemplate , Paragraph , Spacer , Table , TableStyle ,
ListFlowable , ListItem
)
from google.adk.agents import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from clinassist_agent.agent import root_agent
from clinassist_agent.schemas import ClinTriageReport , DISCLAIMER_TEXT

APP_NAME = "clinassist_export"
USER_ID = "export_user"
SESSION_ID = "export_session_001"

async def run_pipeline(query: str) -> dict:
    svc = InMemorySessionService()
    session = await svc.create_session(
    app_name=APP_NAME , user_id=USER_ID , session_id=SESSION_ID
    )
    runner = Runner(
    agent=root_agent , app_name=APP_NAME , session_service=svc
    )
    content = types.Content(
    role="user", parts=[types.Part(text=query)]
    )
    async for _ in runner.run_async(
    user_id=USER_ID , session_id=SESSION_ID , new_message=content
    ):
        pass
    # Auto-confirm so the full pipeline runs in the export script
    confirm_msg = types.Content(
    role="user", parts=[types.Part(text="confirm")]
    )
    async for _ in runner.run_async(
    user_id=USER_ID , session_id=SESSION_ID , new_message=confirm_msg
    ):
        pass
    updated = await svc.get_session(
    app_name=APP_NAME , user_id=USER_ID , session_id=SESSION_ID
    )
    return updated.state

def build_pdf(report: ClinTriageReport , query: str, output_path: str) -> None:
    doc = SimpleDocTemplate(output_path , pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2.5*cm, rightMargin=2.5*cm)
    styles = getSampleStyleSheet()
    story = []
    # Title
    title_style = ParagraphStyle("Title", parent=styles["Title"], textColor=colors.HexColor("#1A3A5C"), fontSize=18, spaceAfter=8)
    story.append(Paragraph("ClinAssist Eye Health Triage Report", title_style))
    sub_style = ParagraphStyle("Sub", parent=styles["Heading2"], textColor=colors.HexColor("#185FA5"))
    body_style = styles["Normal"]
    body_style.fontSize = 10
    body_style.leading = 14
    # Urgency badge colour
    urgency_colours = {
    "low": colors.HexColor("#0F4D2E"),"medium": colors.HexColor("#BA7517"),"urgent": colors.HexColor("#C0392B"),
    }
    urg_colour = urgency_colours.get(report.urgency_level , colors.HexColor("#1A3A5C"))
    # Summary table
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Triage Summary", sub_style))
    summary_data = [
    ["Query", query],
    ["Urgency Level", report.urgency_level.upper()],
    ["Symptom Summary", report.symptom_summary],
    ["Recommendation", report.triage_recommendation],
    ]
    tbl = Table(summary_data, colWidths=[4*cm, 12*cm])
    tbl.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF1FB")),
    ("BACKGROUND", (1, 1), (1, 1), urg_colour),
    ("TEXTCOLOR", (1, 1), (1, 1), colors.white),
    ("FONTNAME", (0, 0), (0, -1), "Helvetica -Bold"),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#185FA5")),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING",(0, 0), (-1, -1), 5),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 0.5*cm))
    # Evidence
    story.append(Paragraph("Retrieved Evidence", sub_style))
    for ev in report.retrieved_evidence:
        story.append(Paragraph(f"- {ev}", body_style))
    story.append(Spacer(1, 0.2*cm))
    # Sources
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph("Sources", sub_style))
    story.append(Paragraph(", ".join(report.sources), body_style))
    # Disclaimer
    story.append(Spacer(1, 0.5*cm))
    disc_style = ParagraphStyle("Disc", parent=styles["Normal"], fontSize=8, textColor=colors.gray , borderColor=colors.HexColor("#C0392B"), borderWidth=0.5, borderPadding=6, backColor=colors.HexColor("#FFF0F0"))
    story.append(Paragraph(report.disclaimer , disc_style))
    doc.build(story)
    print(f"PDF saved: {output_path}")

async def main() -> None:
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "I have a red eye with discharge and it feels gritty."
    print(f"Running ClinAssist pipeline for: ’{query}’")
    state = await run_pipeline(query)
    raw = state.get("triage_report", "")
    if not raw:
        print("[ERROR] No triage_report found in state. Did the pipeline complete?")
        return
    try:
        report = ClinTriageReport(**json.loads(raw))
    except Exception as e:
        print(f"[ERROR] Report validation failed: {e}")
        return
    build_pdf(report, query, f"clinassist_report.pdf")

if __name__ == "__main__":
    asyncio.run(main())
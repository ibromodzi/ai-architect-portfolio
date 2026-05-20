# export_report.py
# Reads the risk_report and judge_score from session state and exports a formatted PDF.
# Run with: python export_report.py
# reportlab docs: https://docs.reportlab.com/

import asyncio
import json
from pathlib import Path
from dotenv import load_dotenv

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

from finsight_agent.agent import root_agent

load_dotenv("finsight_agent/.env")

APP_NAME = "finsight_export"
USER_ID = "export_user"
SESSION_ID = "export_session_001"


async def run_pipeline(ticker: str) -> dict:
    """Run the full FinSight pipeline and return session state."""
    svc = InMemorySessionService()
    session = await svc.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    runner = Runner(agent=root_agent, app_name=APP_NAME, session_service=svc)

    content = types.Content(
        role="user", parts=[types.Part(text=f"Analyse the risk for {ticker}")]
    )

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    ):
        pass  # consume all events; state is updated as side effect

    updated = await svc.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    return updated.state


def build_pdf(state: dict, ticker: str, output_path: str) -> None:
    """Build a formatted PDF from the risk report state."""
    risk_raw = state.get("risk_report", "{}")
    judge_raw = state.get("judge_score", "{}")

    try:
        risk = json.loads(risk_raw)
    except (json.JSONDecodeError, TypeError):
        risk = {"error": "Could not parse risk report"}

    try:
        judge = json.loads(judge_raw)
    except (json.JSONDecodeError, TypeError):
        judge = {"score": "N/A", "reasoning": "N/A", "pass_fail": "N/A"}

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        textColor=colors.HexColor("#1A3A5C"),
        fontSize=20,
        spaceAfter=12,
    )
    story.append(Paragraph(f"FinSight Risk Report: {ticker}", title_style))
    story.append(Spacer(1, 0.4 * cm))

    # Risk report table
    sub_style = ParagraphStyle(
        "Sub", parent=styles["Heading2"], textColor=colors.HexColor("#185FA5")
    )
    story.append(Paragraph("Risk Assessment", sub_style))
    story.append(Spacer(1, 0.2 * cm))

    # Wrapping Table cells in Paragraphs ensures clean text wrapping for long summaries
    body_style = styles["Normal"]
    report_data = [
        ["Field", "Value"],
        ["Ticker", risk.get("ticker", "N/A")],
        ["Risk Level", risk.get("risk_level", "N/A")],
        ["Volatility (%)", str(risk.get("volatility_pct", "N/A"))],
        ["PE Ratio", str(risk.get("pe_ratio", "N/A"))],
        ["Summary", Paragraph(risk.get("summary", "N/A"), body_style)],
        ["Recommendation", risk.get("recommendation", "N/A")],
    ]

    tbl = Table(report_data, colWidths=[5 * cm, 11 * cm])
    tbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1A3A5C")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.HexColor("#EAF1FB"), colors.white],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#185FA5")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(tbl)
    story.append(Spacer(1, 0.6 * cm))

    # Judge score table
    story.append(Paragraph("Quality Evaluation", sub_style))
    story.append(Spacer(1, 0.2 * cm))

    judge_data = [
        ["Score", "Pass/Fail", "Reasoning"],
        [
            str(judge.get("score", "N/A")),
            str(judge.get("pass_fail", "N/A")),
            Paragraph(str(judge.get("reasoning", "N/A")), body_style),
        ],
    ]

    jtbl = Table(judge_data, colWidths=[2.5 * cm, 3 * cm, 10.5 * cm])
    jtbl.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0F4D2E")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#E1F5EE")]),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#0F6E56")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("FONTSIZE", (0, 1), (-1, -1), 9),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(jtbl)
    story.append(Spacer(1, 0.6 * cm))

    # Footer
    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"], fontSize=8, textColor=colors.gray
    )
    story.append(
        Paragraph("Generated by FinSight v1.0 --- ADK Sprint Day 6", footer_style)
    )

    doc.build(story)
    print(f"PDF saved to: {output_path}")


async def main() -> None:
    ticker = "AAPL"
    print(f"Running FinSight pipeline for {ticker}...")
    state = await run_pipeline(ticker)
    print(f"Pipeline complete. State keys: {list(state.keys())}")

    build_pdf(state, ticker, f"finsight_report_{ticker}.pdf")


if __name__ == "__main__":
    asyncio.run(main())
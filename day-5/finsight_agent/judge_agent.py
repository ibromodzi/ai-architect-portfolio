# # finsight_agent/judge_agent.py
# # LLM-as-judge pattern for scoring RiskReport quality.

# from google.adk.agents import LlmAgent
# from pydantic import BaseModel, Field


# class JudgeScore(BaseModel):
#     score: int = Field(
#         description="Quality score from 1 (worst) to 5 (best)."
#     )
#     reasoning: str = Field(description="One sentence justifying the score.")
#     pass_fail: str = Field(
#         description="'pass' if score >= 3, otherwise 'fail'."
#     )


# judge_agent = LlmAgent(
#     name="RiskReportJudge",
#     # model="gemini-2.5-flash",
#     model="gemini-2.0-flash",  # cheaper model for faster iteration; upgrade to 2.5 for better quality
#     description=(
#         "Evaluates the quality of a FinSight risk report against a rubric. "
#         "Use after RiskAssessorAgent has produced a report."
#     ),
#     instruction=(
#         "You are a senior quantitative analyst evaluating AI-generated "
#         "risk reports for quality and completeness.\n\n"
#         "Report to evaluate:\n{risk_report}\n\n"
#         "Score this report from 1 to 5 using the following rubric:\n"
#         "5 - All fields present with real numeric data; recommendation clear.\n"
#         "4 - Minor omissions (e.g. PE ratio N/A); recommendation present.\n"
#         "3 - Most fields correct; recommendation vague or generic.\n"
#         "2 - Key numeric fields missing (price, volatility); N/A values.\n"
#         "1 - Report empty, all N/A, or clearly hallucinated.\n\n"
#         "Respond with a JSON object matching the required schema exactly."
#     ),
#     output_schema=JudgeScore,
#     output_key="judge_score",
# )

# finsight_agent/judge_agent.py
# LLM-as-judge pattern for scoring RiskReport quality.

from google.adk.agents import LlmAgent
from google.genai import types
from pydantic import BaseModel, Field

# -----------------------------------------------------------
# SHARED RETRY CONFIG (mirrors agent.py)
# -----------------------------------------------------------
RETRY_CONFIG = types.GenerateContentConfig(
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            initial_delay=5,
            attempts=4,
        ),
    )
)


class JudgeScore(BaseModel):
    score: int = Field(
        description="Quality score from 1 (worst) to 5 (best)."
    )
    reasoning: str = Field(description="One sentence justifying the score.")
    pass_fail: str = Field(
        description="'pass' if score >= 3, otherwise 'fail'."
    )


judge_agent = LlmAgent(
    name="RiskReportJudge",
    model="gemini-2.0-flash",  # upgrade to gemini-2.5-flash for better quality
    description=(
        "Evaluates the quality of a FinSight risk report against a rubric. "
        "Use after RiskAssessorAgent has produced a report."
    ),
    instruction=(
        "You are a senior quantitative analyst evaluating AI-generated "
        "risk reports for quality and completeness.\n\n"
        "Report to evaluate:\n{risk_report}\n\n"
        "Score this report from 1 to 5 using the following rubric:\n"
        "5 - All fields present with real numeric data; recommendation clear.\n"
        "4 - Minor omissions (e.g. PE ratio N/A); recommendation present.\n"
        "3 - Most fields correct; recommendation vague or generic.\n"
        "2 - Key numeric fields missing (price, volatility); N/A values.\n"
        "1 - Report empty, all N/A, or clearly hallucinated.\n\n"
        "Respond with a JSON object matching the required schema exactly."
    ),
    output_schema=JudgeScore,
    output_key="judge_score",
    generate_content_config=RETRY_CONFIG,
)
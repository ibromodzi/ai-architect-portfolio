# # # finsight_agent/agent.py
# # # Day 4: Multi-Agent Orchestration --- FinSight v0.1
# # #
# # # Official multi-agent docs:
# # # https://google.github.io/adk-docs/agents/multi-agents/
# # # Official agent team tutorial:
# # # https://google.github.io/adk-docs/tutorials/agent-team/

# # from google.adk.agents import LlmAgent
# # from .tools import get_market_data

# # # -----------------------------------------------------------
# # # DATA-FETCHER SUB-AGENT
# # # Description is the primary signal AutoFlow uses to decide when
# # # to delegate to this agent. Be precise and distinct.
# # # Official docs: https://google.github.io/adk-docs/agents/multi-agents/#b-llm-driven-delegation-agent-transfer
# # # -----------------------------------------------------------

# # data_fetcher_agent = LlmAgent(
# #     name="DataFetcherAgent",
# #     model="gemini-2.5-flash",
# #     description=(
# #         "Fetches real-time market data (price, volume, market cap, "
# #         "52-week range) for a given stock or crypto ticker symbol. "
# #         "Use this for any query about current or recent market data."
# #     ),
# #     instruction=(
# #         "You are a specialist data-fetcher agent. "
# #         "Your ONLY task is to retrieve market data for the ticker "
# #         "provided by the orchestrator using the get_market_data tool. "
# #         "Return the raw data clearly. Do not analyse or interpret it."
# #     ),
# #     tools=[get_market_data],
# #     output_key="market_data",  # saves response to state['market_data']
# # )

# # # -----------------------------------------------------------
# # # ORCHESTRATOR (ROOT AGENT)
# # # Must be named root_agent for adk web / adk run to discover it.
# # # Official project structure: https://adk.dev/tutorials/multi-tool-agent/
# # # -----------------------------------------------------------

# # root_agent = LlmAgent(
# #     name="FinSightOrchestrator",
# #     model="gemini-2.5-flash",
# #     description="FinSight orchestrator: answers finance queries by delegating data retrieval to specialist sub-agents.",
# #     instruction=(
# #         "You are the FinSight finance assistant. "
# #         "When the user asks about stock prices, market data, or "
# #         "financial metrics for a specific ticker, delegate the data "
# #         "retrieval task to DataFetcherAgent. "
# #         "Once you receive the market data, summarise it clearly for "
# #         "the user: include the current price, day range, volume, "
# #         "market cap, and any notable observations. "
# #         "If the user asks something unrelated to market data, "
# #         "respond helpfully or explain what FinSight can do."
# #     ),
# #     sub_agents=[data_fetcher_agent],  # AutoFlow delegation enabled
# # )


# # finsight_agent/agent.py (updated for FinSight v0.2)
# # Official planner docs: https://google.github.io/adk-docs/agents/llm-agents/#planner
# # Official output_schema docs: https://google.github.io/adk-docs/agents/llm-agents/#structuring-data-input_schema-output_schema-
# # Official SequentialAgent docs: https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/

# from dotenv import load_dotenv
# from google.adk.agents import LlmAgent, SequentialAgent
# from google.adk.planners import PlanReActPlanner
# from pydantic import BaseModel, Field

# from .tools import get_market_data

# load_dotenv("finsight_agent/.env")


# # ---- RiskReport schema ----
# class RiskReport(BaseModel):
#     ticker: str = Field(description="Stock ticker symbol.")
#     risk_level: str = Field(description="'low', 'moderate', or 'high'.")
#     volatility_pct: float = Field(
#         description="52-week range as % of current price."
#     )
#     pe_ratio: str = Field(description="PE ratio or 'N/A'.")
#     summary: str = Field(description="One-sentence risk assessment.")
#     recommendation: str = Field(description="'hold', 'watch', or 'avoid'.")


# # -----------------------------------------------------------
# # SUB-AGENT 1: DATA FETCHER
# # Fetches raw market data and saves to state['market_data'].
# # Has tools; NO output_schema (incompatible combination).
# # -----------------------------------------------------------
# # data_fetcher_agent = LlmAgent(
# #     name="DataFetcherAgent",
# #     model="gemini-2.5-flash",
# #     description=(
# #         "Fetches real-time market data for a given stock or crypto ticker. "
# #         "Use for any query requiring current price, volume, or market cap."
# #     ),
# #     instruction=(
# #         "You are a data-fetcher specialist. "
# #         "Use get_market_data to retrieve data for the ticker in the user query. "
# #         "Return the raw result. Do not interpret or analyse it."
# #     ),
# #     tools=[get_market_data],
# #     output_key="market_data",  # saves raw response to state
# # )

# data_fetcher_agent = LlmAgent(
#     name="DataFetcherAgent",
#     # model="gemini-2.5-flash",
#     model="gemini-2.0-flash",  # cheaper model for faster iteration; upgrade to 2.5 for better quality
#     description=(
#         "Fetches real-time market data for a given stock or crypto ticker. "
#         "Use for any query requiring current price, volume, or market cap."
#     ),
#     instruction=(
#         "You are a data-fetcher specialist. "
#         "Use get_market_data to retrieve data for the ticker in the user query. "
#         "Return ONLY the raw JSON result from the tool, with no additional text, "
#         "explanation, or formatting. Your entire response must be just the JSON."
#     ),
#     tools=[get_market_data],
#     output_key="market_data",
# )

# # -----------------------------------------------------------
# # SUB-AGENT 2: RISK ASSESSOR
# # Reads state['market_data'], reasons with PlanReActPlanner,
# # outputs a structured JSON RiskReport.
# # NO tools --- required by output_schema compatibility constraint.
# # -----------------------------------------------------------
# # risk_assessor_agent = LlmAgent(
# #     name="RiskAssessorAgent",
# #     model="gemini-2.5-flash",
# #     description=(
# #         "Analyses market data from state and produces a structured "
# #         "JSON risk report. Does not fetch data itself."
# #     ),
# #     instruction=(
# #         "You are a quantitative risk analyst. "
# #         "The market data for analysis is available in state: {market_data}. "
# #         "Reason through the following steps before producing your report:\n"
# #         "1. Extract ticker, current price, 52-week high and low.\n"
# #         "2. Compute volatility as (52w_high - 52w_low) / current_price * 100.\n"
# #         "3. Classify risk: >60% = high, 30-60% = moderate, <30% = low.\n"
# #         "4. Note the PE ratio if available.\n"
# #         "5. Write a one-sentence summary and a recommendation.\n"
# #         "Produce a JSON report matching the required schema exactly."
# #     ),
# #     planner=PlanReActPlanner(),  # explicit reasoning steps in output
# #     output_schema=RiskReport,  # enforces typed JSON
# #     output_key="risk_report",  # saves JSON string to state
# #     include_contents="none",  # stateless: reads only from state
# # )

# risk_assessor_agent = LlmAgent(
#     name="RiskAssessorAgent",
#     # model="gemini-2.5-flash",
#     model="gemini-2.0-flash",  # cheaper model for faster iteration; upgrade to 2.5 for better quality
#     description=(
#         "Analyses market data from state and produces a structured "
#         "JSON risk report. Does not fetch data itself."
#     ),
#     instruction=(
#         "You are a quantitative risk analyst. "
#         "The raw market data JSON is: {market_data}\n\n"
#         "Extract these values from the JSON above:\n"
#         "- ticker: from data.ticker\n"
#         "- current_price: from data.current_price\n"
#         "- 52_week_high: from data.52_week_high\n"
#         "- 52_week_low: from data.52_week_low\n"
#         "- pe_ratio: from data.pe_ratio (use 'N/A' if null)\n\n"
#         "Then compute:\n"
#         "- volatility_pct = (52_week_high - 52_week_low) / current_price * 100\n"
#         "- risk_level: >60 = high, 30-60 = moderate, <30 = low\n"
#         "- recommendation: high=avoid, moderate=watch, low=hold\n"
#         "- summary: one sentence describing the risk\n\n"
#         "Produce the JSON report matching the required schema exactly."
#     ),
#     planner=PlanReActPlanner(),
#     output_schema=RiskReport,
#     output_key="risk_report",
#     include_contents="none",
# )

# # -----------------------------------------------------------
# # SEQUENTIAL PIPELINE (FinSight v0.2)
# # Step 1: DataFetcherAgent fetches data -> saves to state['market_data']
# # Step 2: RiskAssessorAgent reads state, reasons, produces report
# # -----------------------------------------------------------
# # root_agent = SequentialAgent(
# #     name="FinSightPipeline",
# #     description=(
# #         "FinSight v0.2: fetches market data then produces a structured "
# #         "JSON risk report end-to-end."
# #     ),
# #     sub_agents=[data_fetcher_agent, risk_assessor_agent],
# # )
# # In finsight_agent/agent.py, update the root_agent SequentialAgent:
# from .judge_agent import judge_agent

# root_agent = SequentialAgent(
#     name="FinSightPipeline",
#     description="FinSight v1.0: fetch -> assess risk -> judge quality.",
#     sub_agents=[
#         data_fetcher_agent,  # Step 1: fetch market data
#         risk_assessor_agent,  # Step 2: produce JSON risk report
#         judge_agent,  # Step 3: grade report quality via LLM-as-judge
#     ],
# )


# finsight_agent/agent.py (FinSight v1.0 + retry config)
# Official planner docs: https://google.github.io/adk-docs/agents/llm-agents/#planner
# Official output_schema docs: https://google.github.io/adk-docs/agents/llm-agents/#structuring-data-input_schema-output_schema-
# Official SequentialAgent docs: https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/
# Retry docs: https://google.github.io/adk-docs/agents/models/google-gemini/#error-code-429-resource_exhausted

from dotenv import load_dotenv
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.planners import PlanReActPlanner
from google.genai import types
from pydantic import BaseModel, Field

from .tools import get_market_data

load_dotenv("finsight_agent/.env")

# -----------------------------------------------------------
# SHARED RETRY CONFIG
# Applies to all agents to handle 429 / RESOURCE_EXHAUSTED.
# initial_delay: seconds before first retry (doubles each attempt).
# attempts: total number of tries (1 original + N-1 retries).
# -----------------------------------------------------------
RETRY_CONFIG = types.GenerateContentConfig(
    http_options=types.HttpOptions(
        retry_options=types.HttpRetryOptions(
            initial_delay=5,   # wait 5s before first retry
            attempts=4,        # 1 original + 3 retries (5s, 10s, 20s backoff)
        ),
    )
)


# ---- RiskReport schema ----
class RiskReport(BaseModel):
    ticker: str = Field(description="Stock ticker symbol.")
    risk_level: str = Field(description="'low', 'moderate', or 'high'.")
    volatility_pct: float = Field(
        description="52-week range as % of current price."
    )
    pe_ratio: str = Field(description="PE ratio or 'N/A'.")
    summary: str = Field(description="One-sentence risk assessment.")
    recommendation: str = Field(description="'hold', 'watch', or 'avoid'.")


# -----------------------------------------------------------
# SUB-AGENT 1: DATA FETCHER
# Fetches raw market data and saves to state['market_data'].
# Has tools; NO output_schema (incompatible combination).
# -----------------------------------------------------------
data_fetcher_agent = LlmAgent(
    name="DataFetcherAgent",
    model="gemini-2.0-flash",  # upgrade to gemini-2.5-flash for better quality
    description=(
        "Fetches real-time market data for a given stock or crypto ticker. "
        "Use for any query requiring current price, volume, or market cap."
    ),
    instruction=(
        "You are a data-fetcher specialist. "
        "Use get_market_data to retrieve data for the ticker in the user query. "
        "Return ONLY the raw JSON result from the tool, with no additional text, "
        "explanation, or formatting. Your entire response must be just the JSON."
    ),
    tools=[get_market_data],
    output_key="market_data",
    generate_content_config=RETRY_CONFIG,
)

# -----------------------------------------------------------
# SUB-AGENT 2: RISK ASSESSOR
# Reads state['market_data'], reasons with PlanReActPlanner,
# outputs a structured JSON RiskReport.
# NO tools --- required by output_schema compatibility constraint.
# -----------------------------------------------------------
risk_assessor_agent = LlmAgent(
    name="RiskAssessorAgent",
    model="gemini-2.0-flash",  # upgrade to gemini-2.5-flash for better quality
    description=(
        "Analyses market data from state and produces a structured "
        "JSON risk report. Does not fetch data itself."
    ),
    instruction=(
        "You are a quantitative risk analyst. "
        "The raw market data JSON is: {market_data}\n\n"
        "Extract these values from the JSON above:\n"
        "- ticker: from data.ticker\n"
        "- current_price: from data.current_price\n"
        "- 52_week_high: from data.52_week_high\n"
        "- 52_week_low: from data.52_week_low\n"
        "- pe_ratio: from data.pe_ratio (use 'N/A' if null)\n\n"
        "Then compute:\n"
        "- volatility_pct = (52_week_high - 52_week_low) / current_price * 100\n"
        "- risk_level: >60 = high, 30-60 = moderate, <30 = low\n"
        "- recommendation: high=avoid, moderate=watch, low=hold\n"
        "- summary: one sentence describing the risk\n\n"
        "Produce the JSON report matching the required schema exactly."
    ),
    planner=PlanReActPlanner(),
    output_schema=RiskReport,
    output_key="risk_report",
    include_contents="none",
    generate_content_config=RETRY_CONFIG,
)

# -----------------------------------------------------------
# SEQUENTIAL PIPELINE (FinSight v1.0)
# Step 1: DataFetcherAgent  -> state['market_data']
# Step 2: RiskAssessorAgent -> state['risk_report']
# Step 3: JudgeAgent        -> state['judge_score']
# -----------------------------------------------------------
from .judge_agent import judge_agent

root_agent = SequentialAgent(
    name="FinSightPipeline",
    description="FinSight v1.0: fetch -> assess risk -> judge quality.",
    sub_agents=[
        data_fetcher_agent,
        risk_assessor_agent,
        judge_agent,
    ],
)
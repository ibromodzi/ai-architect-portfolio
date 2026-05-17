# finsight_agent/agent.py
# Day 4: Multi-Agent Orchestration --- FinSight v0.1
#
# Official multi-agent docs:
# https://google.github.io/adk-docs/agents/multi-agents/
# Official agent team tutorial:
# https://google.github.io/adk-docs/tutorials/agent-team/

from google.adk.agents import LlmAgent
from .tools import get_market_data

# -----------------------------------------------------------
# DATA-FETCHER SUB-AGENT
# Description is the primary signal AutoFlow uses to decide when
# to delegate to this agent. Be precise and distinct.
# Official docs: https://google.github.io/adk-docs/agents/multi-agents/#b-llm-driven-delegation-agent-transfer
# -----------------------------------------------------------

data_fetcher_agent = LlmAgent(
    name="DataFetcherAgent",
    model="gemini-2.5-flash",
    description=(
        "Fetches real-time market data (price, volume, market cap, "
        "52-week range) for a given stock or crypto ticker symbol. "
        "Use this for any query about current or recent market data."
    ),
    instruction=(
        "You are a specialist data-fetcher agent. "
        "Your ONLY task is to retrieve market data for the ticker "
        "provided by the orchestrator using the get_market_data tool. "
        "Return the raw data clearly. Do not analyse or interpret it."
    ),
    tools=[get_market_data],
    output_key="market_data",  # saves response to state['market_data']
)

# -----------------------------------------------------------
# ORCHESTRATOR (ROOT AGENT)
# Must be named root_agent for adk web / adk run to discover it.
# Official project structure: https://adk.dev/tutorials/multi-tool-agent/
# -----------------------------------------------------------

root_agent = LlmAgent(
    name="FinSightOrchestrator",
    model="gemini-2.5-flash",
    description="FinSight orchestrator: answers finance queries by delegating data retrieval to specialist sub-agents.",
    instruction=(
        "You are the FinSight finance assistant. "
        "When the user asks about stock prices, market data, or "
        "financial metrics for a specific ticker, delegate the data "
        "retrieval task to DataFetcherAgent. "
        "Once you receive the market data, summarise it clearly for "
        "the user: include the current price, day range, volume, "
        "market cap, and any notable observations. "
        "If the user asks something unrelated to market data, "
        "respond helpfully or explain what FinSight can do."
    ),
    sub_agents=[data_fetcher_agent],  # AutoFlow delegation enabled
)
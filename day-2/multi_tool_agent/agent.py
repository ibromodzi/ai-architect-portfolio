# multi_tool_agent/agent.py

# Following the official ADK multi-tool agent tutorial:
# https://adk.dev/tutorials/multi-tool-agent/

# from google.adk.agents import Agent
# from .tools import calculate, convert_units, format_timestamp

# # -----------------------------------------------------------
# # SYSTEM PROMPT drives tool-selection reasoning
# # -----------------------------------------------------------

# SYSTEM_PROMPT = """
# You are a precise utility assistant with access to three tools:
# - calculate: for arithmetic and mathematical expressions
# - convert_units: for physical unit conversions
# - format_timestamp: for converting Unix timestamps to readable dates

# Always use a tool when the user request maps to one. Never estimate 
# or calculate mentally—always call the appropriate tool. 

# If a request does not map to any available tool, say so clearly and explain why.
# """

# # -----------------------------------------------------------
# # ROOT AGENT must be named 'root_agent' for adk web / adk run
# # -----------------------------------------------------------

# root_agent = Agent(
#     name="multi_tool_agent",
#     model="gemini-2.5-flash",  # Use gemini-2.5-flash per current docs
#     description=(
#         "A utility agent for maths, unit conversion, and timestamp formatting."
#     ),
#     instruction=SYSTEM_PROMPT,
#     tools=[calculate, convert_units, format_timestamp],
# )


# Add to multi_tool_agent/agent.py (replace root_agent definition)
# Official ADK structured output docs:
# https://adk.dev/tools-custom/function-tools/

import typing_extensions as typing
from google.adk.agents import Agent
from .tools import calculate, convert_units, format_timestamp

# Define the expected output shape
class ToolResponse(typing.TypedDict):
    tool_used: str     # Name of the tool called, or "none"
    input_query: str   # The user’s original query
    result: str        # Human-readable result
    raw_output: dict   # The dict returned by the tool

SYSTEM_PROMPT = """
You are a precise utility assistant with access to three tools:
- calculate: for arithmetic and mathematical expressions
- convert_units: for physical unit conversions
- format_timestamp: for converting Unix timestamps to readable dates

Always use a tool when the user request maps to one. Never estimate 
or calculate mentally. Always respond in the specified JSON schema.
"""

# Must still be named root_agent for adk web / adk run to discover it
root_agent = Agent(
    name="multi_tool_agent",
    model="gemini-2.5-flash",
    description=(
        "A utility agent for maths, unit conversion, and timestamp formatting."
    ),
    instruction=SYSTEM_PROMPT,
    tools=[calculate, convert_units, format_timestamp],
    output_schema=ToolResponse,
    output_key="tool_response",
)
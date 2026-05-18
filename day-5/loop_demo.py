# loop_demo.py (run from the day folder with: python loop_demo.py)
# Demonstrates LoopAgent with max_iterations hard limit and exit_loop soft stop.
# Official docs: https://google.github.io/adk-docs/agents/workflow-agents/loop-agents/

import asyncio
from dotenv import load_dotenv
from google.adk.agents import LlmAgent, LoopAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.tool_context import ToolContext
from google.genai import types

load_dotenv("finsight_agent/.env")

APP_NAME = "loop_demo"
USER_ID = "dev"
SESSION_ID = "loop_s1"


# ---- Soft-stop tool ----
def exit_loop(tool_context: ToolContext) -> dict:
    """Call this ONLY when the risk report is complete and satisfactory.

    Signals the LoopAgent to stop iterating.
    """
    print(
        "[exit_loop] Escalating --- loop will stop after this iteration."
    )
    tool_context.actions.escalate = True
    return {}


# ---- Iterative refiner agent ----
refiner = LlmAgent(
    name="ReportRefiner",
    model="gemini-2.5-flash",
    instruction=(
        "You are refining a draft risk report stored in {draft_report}. "
        "Improve it by one step. If it is already clear, concise, and complete, "
        "call exit_loop to signal you are done. "
        "Otherwise output the improved report text."
    ),
    tools=[exit_loop],
    output_key="draft_report",
    include_contents="none",
)


# ---- LoopAgent with BOTH safeguards ----
loop = LoopAgent(
    name="RefinementLoop",
    max_iterations=3,  # hard limit --- loop stops here regardless
    sub_agents=[refiner],  # soft stop via exit_loop tool
)


async def run() -> None:
    svc = InMemorySessionService()
    session = await svc.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=SESSION_ID,
        state={
            "draft_report": "AAPL risk: moderate. Volatility is significant."
        },
    )

    runner = Runner(agent=loop, app_name=APP_NAME, session_service=svc)

    content = types.Content(
        role="user", parts=[types.Part(text="Refine the risk report.")]
    )

    async for event in runner.run_async(
        user_id=USER_ID, session_id=SESSION_ID, new_message=content
    ):
        if event.is_final_response() and event.content:
            print("Final:", event.content.parts[0].text)

    updated = await svc.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("Draft in state:", updated.state.get("draft_report"))


if __name__ == "__main__":
    asyncio.run(run())
# tests/test_finsight.py
# Official ADK eval docs: https://adk.dev/evaluate/#2-pytest-run-tests-programmatically

# import pytest
# from google.adk.evaluation.agent_evaluator import AgentEvaluator


# @pytest.mark.asyncio
# async def test_finsight_tool_trajectory():
#     """Verifies that DataFetcherAgent calls get_market_data for each ticker

#     and that the final response contains key risk report fields.

#     Criteria: tool_trajectory_avg_score=1.0, response_match_score=0.5
#     """
#     # await AgentEvaluator.evaluate(
#     #     agent_module="finsight_agent",
#     #     eval_dataset_file_path_or_dir="tests/finsight_eval.test.json",
#     #     config_file_path="tests/test_config.json",
#     # )
#     await AgentEvaluator.evaluate(
#     agent_module="finsight_agent",
#     eval_dataset_file_path_or_dir="tests/finsight_eval.test.json",
#     print_detailed_results=True,
# )

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

@pytest.mark.asyncio
async def test_finsight_tool_trajectory():
    """
    Verifies that DataFetcherAgent calls get_market_data for each ticker
    and that the final response contains key risk report fields.
    """
    await AgentEvaluator.evaluate(
        agent_module="finsight_agent",
        eval_dataset_file_path_or_dir="tests/finsight_eval.test.json",
        print_detailed_results=True,
    )
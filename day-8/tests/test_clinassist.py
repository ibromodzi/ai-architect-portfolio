# tests/test_clinassist.py
# Official eval docs: https://adk.dev/evaluate/

import pytest
from google.adk.evaluation.agent_evaluator import AgentEvaluator

@pytest.mark.asyncio
async def test_clinassist_pipeline():
    """
    Five-case eval: tool trajectory + response match for happy path
    and safety cases. num_runs=1 to respect free-tier quota.
    """
    await AgentEvaluator.evaluate(
        agent_module="clinassist_agent",
        eval_dataset_file_path_or_dir="tests/clinassist_eval.test.json",
        num_runs=1,
        print_detailed_results=True,
    )
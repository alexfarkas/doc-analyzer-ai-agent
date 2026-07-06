from typing import Callable, Awaitable

from agent.models.agent_analysis_data import AgentAnalysisData
from api.models.analisys.result_data import ResultData
from llm.tokens.total_token_usage_utils import update_and_get_total_token_usage


async def build_clarify_chat_result(
    agent_call: Callable[[], Awaitable[AgentAnalysisData]],
    response_model,
):
    result = await agent_call()
    total_token_usage = await update_and_get_total_token_usage(result.token_usage)
    return response_model(
        result=ResultData(answer_seq=result.answer_seq),
        elapsed=result.elapsed,
        token_usage=result.token_usage,
        total_token_usage=total_token_usage,
        cost_rub=result.cost_rub,
    )

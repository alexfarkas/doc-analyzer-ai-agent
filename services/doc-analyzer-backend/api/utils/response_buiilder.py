from itertools import zip_longest
from typing import Callable, Awaitable

from api.models.analisys.result_data import ResultData
from api.utils.total_token_usage_utils import update_and_get_total_token_usage
from llm.token_usage import TokenUsage


def build_agent_analyze_result(
    answer: str,
    elapsed: float,
    token_usage: TokenUsage,
    total_token_usage: TokenUsage,
) -> dict:
    return {
        "result": [
            {
                "answer": answer,
            }
        ],
        "elapsed": elapsed,
        "token_usage": token_usage.model_dump()
        if token_usage
        else None,
        "total_token_usage": total_token_usage.model_dump(),
    }


def build_council_analyze_result(
    answers: list[str],
    judgements: list[str],
    scores: list[float],
    iterations: list[dict],
    elapsed: float,
    token_usage: TokenUsage,
    total_token_usage: TokenUsage,
) -> dict:
    return {
        "result": [
            {
                "answer": answer,
                "judgement": judgement,
                "score": score,
                "answer_iterations": answer_iterations,
            }
            for answer, judgement, score, answer_iterations in zip_longest(
                answers,
                judgements,
                scores,
                iterations,
                fillvalue=None,
            )
        ],
        "elapsed": elapsed,
        "token_usage": token_usage.model_dump()
        if token_usage
        else None,
        "total_token_usage": total_token_usage.model_dump(),
    }


async def build_clarify_chat_result(
    agent_call: Callable[[], Awaitable[dict]],
    response_model,
):
    result = await agent_call()
    total_token_usage = await update_and_get_total_token_usage(result["token_usage"])
    return response_model(
        result=ResultData(answer=result["answer"]),
        elapsed=result["elapsed"],
        token_usage=result["token_usage"],
        total_token_usage=total_token_usage,
        cost_rub=result["cost_rub"],
    )

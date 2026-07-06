from itertools import zip_longest
from typing import Callable, Awaitable

from api.models.analisys.answer_seq import AnswerSeq
from api.models.analisys.result_data import ResultData
from api.utils.total_token_usage_utils import update_and_get_total_token_usage
from llm.token_usage import TokenUsage


def build_agent_analyze_result(
    answer_seq: AnswerSeq,
    elapsed: float,
    token_usage: TokenUsage,
    total_token_usage: TokenUsage,
) -> dict:
    return {
        "result": [
            {
                "answer_seq": answer_seq,
            }
        ],
        "elapsed": elapsed,
        "token_usage": token_usage.model_dump()
        if token_usage
        else None,
        "total_token_usage": total_token_usage.model_dump(),
    }


def build_council_analyze_result(
    answer_seqs: list[AnswerSeq],
    judgements: list[str],
    scores: list[float],
    elapsed: float,
    token_usage: TokenUsage,
    total_token_usage: TokenUsage,
) -> dict:
    return {
        "result": [
            {
                "answer_seq": answer_seq.model_dump(),
                "judgement": judgement,
                "score": score,
            }
            for answer_seq, judgement, score in zip_longest(
                answer_seqs,
                judgements,
                scores,
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
        result=ResultData(answer_seq=result["answer_seq"]),
        elapsed=result["elapsed"],
        token_usage=result["token_usage"],
        total_token_usage=total_token_usage,
        cost_rub=result["cost_rub"],
    )

from itertools import zip_longest
from typing import Callable, Awaitable

from agent.models.agent_analysis_data import AgentAnalysisData
from api.models.analisys.analyze_doc_response import AnalyzeDocResponse
from api.models.analisys.answer_item import AnswerItem
from api.models.analisys.answer_seq import AnswerSeq
from api.models.analisys.result_data import ResultData
from llm.tokens.token_usage import TokenUsage
from llm.tokens.total_token_usage_utils import update_and_get_total_token_usage


async def build_agent_doc_analysis_result(
    answer_item: AnswerItem,
    token_usage: TokenUsage | None,
    total_token_usage: TokenUsage,
    elapsed: float,
    cost_rub: float = 0,
):
    return AnalyzeDocResponse(
        result=[
            ResultData(
                answer_seq=AnswerSeq(
                    answers=[
                        answer_item.model_dump(),
                    ]
                ),
            ),
        ],
        token_usage=token_usage.model_dump() if token_usage else None,
        total_token_usage=total_token_usage.model_dump(),
        elapsed=elapsed,
        cost_rub=cost_rub,
    ).model_dump()


async def build_council_doc_analysis_result(
    answer_seqs: list[AnswerSeq],
    judgements: list[str],
    scores: list[float | None],
    token_usage: TokenUsage | None,
    total_token_usage: TokenUsage,
    elapsed: float,
    cost_rub: float = 0,
):
    return AnalyzeDocResponse(
        result=[
            ResultData(
                answer_seq=answer_seq.model_dump(),
                judgement=judgement,
                score=score,
            )
            for answer_seq, judgement, score in zip_longest(
                answer_seqs,
                judgements,
                scores,
                fillvalue=None,
            )
        ],
        token_usage=token_usage.model_dump() if token_usage else None,
        total_token_usage=total_token_usage.model_dump(),
        elapsed=elapsed,
        cost_rub=cost_rub,
    ).model_dump()


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

from itertools import zip_longest
from typing import Callable, Awaitable

from agent_enums import Role

from src.doc_analyzer_backend.agent.models.analysis.agent_analysis_data import (
    AgentAnalysisData,
)
from src.doc_analyzer_backend.agent.models.tokens.consumption_data import (
    ConsumptionData,
)
from src.doc_analyzer_backend.api.models.analisys.analyze_doc_response import (
    AnalyzeDocResponse,
)
from src.doc_analyzer_backend.api.models.analisys.answer_item import AnswerItem
from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq
from src.doc_analyzer_backend.api.models.analisys.result_data import ResultData
from src.doc_analyzer_backend.agent.models.tokens.token_usage import TokenUsage
from src.doc_analyzer_backend.data.utils.total_tokens_cost_utils import (
    update_total_consumption,
)


async def build_agent_doc_analysis_result(
    answer_item: AnswerItem,
    role: Role,
    consumption_data: ConsumptionData,
    total_token_usage: TokenUsage,
    total_cost: float = 0.0,
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
        role=role,
        token_usage=consumption_data.token_usage.model_dump()
        if consumption_data.token_usage
        else None,
        total_token_usage=total_token_usage.model_dump(),
        elapsed=consumption_data.elapsed,
        cost=consumption_data.cost,
        total_cost=total_cost,
    ).model_dump()


async def build_council_doc_analysis_result(
    answer_seqs: list[AnswerSeq],
    role: Role,
    judgements: list[str],
    scores: list[float | None],
    consumption_data: ConsumptionData,
    total_token_usage: TokenUsage,
    total_cost: float = 0.0,
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
        role=role,
        token_usage=consumption_data.token_usage.model_dump()
        if consumption_data.token_usage
        else None,
        total_token_usage=total_token_usage.model_dump(),
        elapsed=consumption_data.elapsed,
        cost=consumption_data.cost,
        total_cost=total_cost,
    ).model_dump()


async def build_clarify_chat_result(
    agent_call: Callable[[], Awaitable[AgentAnalysisData]],
    response_model,
):
    result = await agent_call()
    total_token_usage, total_cost = await update_total_consumption(
        consumption_data=result.consumption_data,
    )
    return response_model(
        result=ResultData(answer_seq=result.answer_seq),
        token_usage=result.consumption_data.token_usage,
        total_token_usage=total_token_usage,
        elapsed=result.consumption_data.elapsed,
        cost=result.consumption_data.cost,
        total_cost=total_cost,
    )

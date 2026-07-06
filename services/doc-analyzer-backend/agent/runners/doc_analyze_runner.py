from itertools import zip_longest

from agent.agent import Agent
from agent.council.council import Council
from api.exceptions.exceptions import AgentsListIsEmptyError
from api.models.analisys.analyze_doc_request import AnalyzeDocRequest
from api.models.analisys.analyze_doc_response import AnalyzeDocResponse
from api.models.analisys.result_data import ResultData
from llm.tokens.total_token_usage_utils import update_and_get_total_token_usage


async def run_doc_analysis(
    request: AnalyzeDocRequest,
    agent: Agent,
    council: Council,
    progress_callback=None,
) -> AnalyzeDocResponse:
    if len(request.agents) == 0:
        raise AgentsListIsEmptyError()

    if len(request.agents) == 1:
        return await _agent_doc_analysis(request, agent, progress_callback)

    return await _council_doc_analysis(request, council, progress_callback)


async def _agent_doc_analysis(
    request: AnalyzeDocRequest,
    agent: Agent,
    progress_callback,
) -> AnalyzeDocResponse:
    if progress_callback:
        await progress_callback(
            "agent_start",
            {
                "agentId": 1,
                "agentType": "exec",
            },
        )

    try:
        result = await agent.analyze_doc(
            resources=request.resources,
            role=request.role,
            model=request.agents[0].model,
            limit=request.limit,
        )

        total_token_usage = await update_and_get_total_token_usage(result.token_usage)

        return AnalyzeDocResponse(
            result=[
                ResultData(
                    answer_seq=result.answer_seq.model_dump(),
                )
            ],
            token_usage=result.token_usage.model_dump() if result.token_usage else None,
            total_token_usage=total_token_usage.model_dump(),
            elapsed=result.elapsed,
            cost_rub=0,
        ).model_dump()

    finally:
        if progress_callback:
            await progress_callback(
                "agent_end",
                {
                    "agentId": 1,
                    "agentType": "exec",
                },
            )


async def _council_doc_analysis(
    request: AnalyzeDocRequest,
    council: Council,
    progress_callback,
) -> AnalyzeDocResponse:
    await council.create_council(request.agents)

    result = await council.analyze_doc(
        resources=request.resources,
        role=request.role,
        limit=request.limit,
        progress_callback=progress_callback,
    )

    total_token_usage = await update_and_get_total_token_usage(result.token_usage)

    return AnalyzeDocResponse(
        result=[
            ResultData(
                answer_seq=answer_seq.model_dump(),
                judgement=judgement,
                score=score,
            )
            for answer_seq, judgement, score in zip_longest(
                result.answer_seqs,
                result.judgements,
                result.scores,
                fillvalue=None,
            )
        ],
        token_usage=result.token_usage.model_dump() if result.token_usage else None,
        total_token_usage=total_token_usage.model_dump(),
        elapsed=result.elapsed,
        cost_rub=0,
    ).model_dump()

from agent_enums import Assignment

from agent.agent import Agent
from agent.council.council import Council
from agent.messages_data.progress_data import start_event, stop_event
from api.exceptions.exceptions import AgentsListIsEmptyError
from api.models.analisys.analyze_doc_request import AnalyzeDocRequest
from api.models.analisys.analyze_doc_response import AnalyzeDocResponse
from api.utils.api_response_builder import (
    build_agent_doc_analysis_result,
    build_council_doc_analysis_result,
)
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
        await progress_callback(start_event(1, Assignment.EXEC))

    try:
        result = await agent.analyze_doc(
            resources=request.resources,
            role=request.role,
            model=request.agents[0].model,
            limit=request.limit,
        )

        total_token_usage = await update_and_get_total_token_usage(result.token_usage)

        return await build_agent_doc_analysis_result(
            answer_item=result.answer_item,
            token_usage=result.token_usage,
            total_token_usage=total_token_usage,
            elapsed=result.elapsed,
            cost_rub=result.cost_rub,
        )

    finally:
        if progress_callback:
            await progress_callback(stop_event(1, Assignment.EXEC))


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

    return await build_council_doc_analysis_result(
        answer_seqs=result.answer_seqs,
        judgements=result.judgements,
        scores=result.scores,
        token_usage=result.token_usage,
        total_token_usage=total_token_usage,
        elapsed=result.elapsed,
    )

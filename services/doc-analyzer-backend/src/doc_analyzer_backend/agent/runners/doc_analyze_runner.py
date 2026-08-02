from agent_enums import Assignment

from src.doc_analyzer_backend.agent.messages_data.progress_data import (
    start_event,
    stop_event,
)
from src.doc_analyzer_backend.api.exceptions.exceptions import AgentsListIsEmptyError
from src.doc_analyzer_backend.api.models.analisys.analyze_doc_request import (
    AnalyzeDocRequest,
)
from src.doc_analyzer_backend.api.models.analisys.analyze_doc_response import (
    AnalyzeDocResponse,
)
from src.doc_analyzer_backend.api.utils.api_response_builder import (
    build_agent_doc_analysis_result,
    build_council_doc_analysis_result,
)
from src.doc_analyzer_backend.session.data.user_session import UserSession


async def run_doc_analysis(
    request: AnalyzeDocRequest,
    user: UserSession,
    progress_callback=None,
) -> AnalyzeDocResponse:
    if len(request.agents) == 0:
        raise AgentsListIsEmptyError()

    if len(request.agents) == 1:
        return await _agent_doc_analysis(request, user, progress_callback)

    return await _council_doc_analysis(request, user, progress_callback)


async def _agent_doc_analysis(
    request: AnalyzeDocRequest,
    user: UserSession,
    progress_callback,
) -> AnalyzeDocResponse:
    if progress_callback:
        await progress_callback(start_event(1, Assignment.EXEC))

    try:
        result = await user.agent.analyze_doc(
            resources=request.resources,
            role=request.role,
            model=request.agents[0].model,
            limit=request.limit,
        )

        await user.data.set_answer_seqs(answer_item=result.answer_item)
        total_token_usage, total_cost = await user.data.update_total_consumption(
            consumption_data=result.consumption_data,
        )

        return await build_agent_doc_analysis_result(
            answer_item=result.answer_item,
            role=request.role,
            consumption_data=result.consumption_data,
            total_token_usage=total_token_usage,
            total_cost=total_cost,
        )

    finally:
        if progress_callback:
            await progress_callback(stop_event(1, Assignment.EXEC))


async def _council_doc_analysis(
    request: AnalyzeDocRequest,
    user: UserSession,
    progress_callback,
) -> AnalyzeDocResponse:
    await user.council.create_council(request.agents)

    result = await user.council.analyze_doc(
        resources=request.resources,
        role=request.role,
        limit=request.limit,
        progress_callback=progress_callback,
    )

    await user.data.set_answer_seqs(answer_seqs=result.answer_seqs)
    total_token_usage, total_cost = await user.data.update_total_consumption(
        consumption_data=result.consumption_data,
    )

    return await build_council_doc_analysis_result(
        answer_seqs=result.answer_seqs,
        role=request.role,
        judgements=result.judgements,
        scores=result.scores,
        consumption_data=result.consumption_data,
        total_token_usage=total_token_usage,
        total_cost=total_cost,
    )

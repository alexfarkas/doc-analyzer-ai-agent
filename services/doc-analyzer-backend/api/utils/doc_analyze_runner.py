from agent.agent import Agent
from agent.council.council import Council
from api.exceptions.exceptions import AgentsListIsEmptyError
from api.models.analisys.analyze_doc_request import AnalyzeDocRequest
from api.utils.response_buiilder import build_agent_analyze_result, build_council_analyze_result
from api.utils.total_token_usage_utils import update_and_get_total_token_usage


async def run_doc_analysis(
    request: AnalyzeDocRequest,
    agent: Agent,
    council: Council,
    progress_callback=None,
) -> dict:
    if len(request.agents) == 0:
        raise AgentsListIsEmptyError()

    if len(request.agents) == 1:
        return await _agent_doc_analysis(request, agent, progress_callback)

    return await _council_doc_analysis(request, council, progress_callback)


async def _agent_doc_analysis(
    request: AnalyzeDocRequest,
    agent: Agent,
    progress_callback,
) -> dict:
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

        total_token_usage = await update_and_get_total_token_usage(result["token_usage"])

        return build_agent_analyze_result(
            answer=result["answer"],
            elapsed=result["elapsed"],
            token_usage=result["token_usage"],
            total_token_usage=total_token_usage,
        )

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
) -> dict:
    await council.create_council(request.agents)

    result = await council.analyze_doc(
        resources=request.resources,
        role=request.role,
        limit=request.limit,
        progress_callback=progress_callback,
    )

    total_token_usage = await update_and_get_total_token_usage(result["token_usage"])

    return build_council_analyze_result(
        answers=result["answers"],
        iterations=result["iterations"],
        judgements=result["judgements"],
        scores=result["scores"],
        elapsed=result["elapsed"],
        token_usage=result["token_usage"],
        total_token_usage=total_token_usage
    )

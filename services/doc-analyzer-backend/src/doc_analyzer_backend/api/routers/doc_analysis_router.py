import asyncio
import json
import logging

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.council.council import Council
from src.doc_analyzer_backend.agent.runners.doc_analyze_runner import run_doc_analysis
from src.doc_analyzer_backend.api.dependencies.dependencies import (
    get_agent,
    get_council, get_user_session,
)
from src.doc_analyzer_backend.api.exceptions.exceptions import AgentsListIsEmptyError
from src.doc_analyzer_backend.api.models.analisys.analyze_doc_request import (
    AnalyzeDocRequest,
)
from src.doc_analyzer_backend.api.models.analisys.analyze_doc_response import (
    AnalyzeDocResponse,
)
from src.doc_analyzer_backend.api.models.analisys.chat_doc_request import ChatDocRequest
from src.doc_analyzer_backend.api.models.analisys.chat_doc_response import (
    ChatDocResponse,
)
from src.doc_analyzer_backend.api.models.analisys.clarify_doc_request import (
    ClarifyDocRequest,
)
from src.doc_analyzer_backend.api.models.analisys.clarify_doc_response import (
    ClarifyDocResponse,
)
from src.doc_analyzer_backend.api.models.analisys.history_response import (
    HistoryResponse,
)
from src.doc_analyzer_backend.api.utils.api_response_builder import (
    build_clarify_chat_result,
    build_agent_doc_analysis_result,
    build_council_doc_analysis_result,
)
from src.doc_analyzer_backend.api.utils.sse_utils import stream_with_queue
from src.doc_analyzer_backend.data.utils.total_tokens_cost_utils import (
    update_total_consumption,
)
from src.doc_analyzer_backend.session.data.user_session import UserSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/doc/analyze", response_model=AnalyzeDocResponse, response_model_exclude_none=True
)
async def api_doc_analyze(
    request: AnalyzeDocRequest,
    agent: Agent = Depends(get_agent),
    council: Council = Depends(get_council),
    user: UserSession = Depends(get_user_session),
):
    if len(request.agents) == 0:
        raise AgentsListIsEmptyError()

    if len(request.agents) == 1:
        result = await agent.analyze_doc(
            resources=request.resources,
            role=request.role,
            model=request.agents[0].model,
        )

        total_token_usage, total_cost = await update_total_consumption(
            consumption_data=result.consumption_data,
        )

        return await build_agent_doc_analysis_result(
            answer_item=result.answer_item,
            role=request.role,
            consumption_data=result.consumption_data,
            total_token_usage=total_token_usage,
            total_cost=total_cost,
        )

    await council.create_council(request.agents)
    result = await council.analyze_doc(resources=request.resources, role=request.role)

    total_token_usage, total_cost = await update_total_consumption(
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


@router.post(
    "/doc/analyze/stream",
    response_model=AnalyzeDocResponse,
    response_model_exclude_none=True,
)
async def api_doc_analyze_stream(
    request: AnalyzeDocRequest,
    agent: Agent = Depends(get_agent),
    council: Council = Depends(get_council),
    user: UserSession = Depends(get_user_session),
):
    event_queue = asyncio.Queue()

    async def progress_callback(event: tuple[str, dict]):
        event_type, data = event
        await event_queue.put(
            {
                "event": event_type,
                "data": data,
            }
        )

    async def run_analysis():
        try:
            final_result = await run_doc_analysis(
                request=request,
                agent=agent,
                council=council,
                progress_callback=progress_callback,
            )
            await event_queue.put(
                {
                    "event": "complete",
                    "data": final_result,
                }
            )
        except Exception as e:
            logger.error(f"Documents analysis error: {e}", exc_info=True)
            await event_queue.put(
                {
                    "event": "error",
                    "data": {
                        "message": str(e),
                    },
                }
            )

    return StreamingResponse(
        stream_with_queue(run_analysis, event_queue),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post(
    "/doc/clarify", response_model=ClarifyDocResponse, response_model_exclude_none=True
)
async def api_clarify_doc(
    request: ClarifyDocRequest,
    agent: Agent = Depends(get_agent),
    user: UserSession = Depends(get_user_session),
):
    async def call_agent():
        return await agent.clarify(
            ai_answer=request.ai_answer,
            user_message=request.user_message,
            answer_index=request.agent_index,
            model=request.model,
        )

    return await build_clarify_chat_result(call_agent, ClarifyDocResponse)


@router.post(
    "/doc/chat", response_model=ChatDocResponse, response_model_exclude_none=True
)
async def api_chat(
    request: ChatDocRequest,
    agent: Agent = Depends(get_agent),
):
    async def call_agent():
        return await agent.chat(user_message=request.user_message, model=request.model)

    return await build_clarify_chat_result(call_agent, ChatDocResponse)


@router.post("/doc/chat/stream")
async def api_chat_stream(
    request: ChatDocRequest,
    agent: Agent = Depends(get_agent),
    user: UserSession = Depends(get_user_session),
):
    async def generate():
        try:
            async for chunk in await agent.chat_stream(
                user_message=request.user_message,
                model=request.model,
            ):
                if chunk.startswith("\n__METADATA__:"):
                    data_json = chunk.replace("\n__METADATA__:", "")
                    yield f"data: {data_json}\n\n"
                else:
                    escaped_token = chunk.replace("\n", "\\n").replace("\r", "\\r")
                    yield f"data: {json.dumps({'token': escaped_token}, ensure_ascii=False)}\n\n"
                    await asyncio.sleep(0.01)
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/doc/history", response_model=HistoryResponse)
async def api_doc_history(
    agent: Agent = Depends(get_agent),
    user: UserSession = Depends(get_user_session),
):
    return HistoryResponse(history=await agent.get_history())

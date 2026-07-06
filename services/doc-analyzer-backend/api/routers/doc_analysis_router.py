import asyncio
import json
import logging

from itertools import zip_longest
from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from agent.agent import Agent
from agent.council.council import Council
from api.dependencies.dependencies import get_agent, get_council
from api.exceptions.exceptions import AgentsListIsEmptyError
from api.models.analisys.analyze_doc_request import AnalyzeDocRequest
from api.models.analisys.analyze_doc_response import AnalyzeDocResponse
from api.models.analisys.chat_doc_request import ChatDocRequest
from api.models.analisys.chat_doc_response import ChatDocResponse
from api.models.analisys.clarify_doc_request import ClarifyDocRequest
from api.models.analisys.clarify_doc_response import ClarifyDocResponse
from api.models.analisys.history_response import HistoryResponse
from api.models.analisys.result_data import ResultData
from agent.runner.doc_analyze_runner import run_doc_analysis
from api.utils.response_buiilder import build_clarify_chat_result
from api.utils.sse_utils import stream_with_queue
from llm.tokens.total_token_usage_utils import update_and_get_total_token_usage

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/doc/analyze", response_model=AnalyzeDocResponse, response_model_exclude_none=True
)
async def api_doc_analyze(
    request: AnalyzeDocRequest,
    agent: Agent = Depends(get_agent),
    council: Council = Depends(get_council),
):
    if len(request.agents) == 0:
        raise AgentsListIsEmptyError()

    if len(request.agents) == 1:
        result = await agent.analyze_doc(
            resources=request.resources, role=request.role, model=request.agents[0].model
        )

        total_token_usage = await update_and_get_total_token_usage(result["token_usage"])

        return AnalyzeDocResponse(
            result=[ResultData(answer_seq=result["answer_seq"])],
            elapsed=result["elapsed"],
            token_usage=result["token_usage"],
            total_token_usage=total_token_usage,
            cost_rub=result["cost_rub"],
        )

    await council.create_council(request.agents)
    result = await council.analyze_doc(
        resources=request.resources, role=request.role
    )

    answer_seqs = result["answer_seqs"]
    judgements = result["judgements"]
    scores = result["scores"]

    total_token_usage = await update_and_get_total_token_usage(result["token_usage"])

    return AnalyzeDocResponse(
        result=[
            ResultData(answer_seq=answer_seq, judgement=judgement, score=score)
            for answer_seq, judgement, score in zip_longest(
                answer_seqs, judgements, scores, fillvalue=None
            )
        ],
        elapsed=result["elapsed"],
        token_usage=result["token_usage"],
        total_token_usage=total_token_usage,
        cost_rub=0,
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
):
    event_queue = asyncio.Queue()

    async def progress_callback(event_type: str, data: dict):
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
):
    async def call_agent():
        return await agent.clarify(
            ai_answer=request.ai_answer,
            user_message=request.user_message,
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
):
    async def generate():
        try:
            async for chunk in agent.chat_stream(
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
async def api_doc_history(agent: Agent = Depends(get_agent)):
    return HistoryResponse(history=await agent.get_history())

import asyncio
import json
import logging
from itertools import zip_longest

from fastapi import APIRouter, Depends
from starlette.responses import StreamingResponse

from agent.agent import Agent
from agent.council.council import Council
from api.dependencies.dependencies import get_agent, get_council, get_app_state
from api.exceptions.exceptions import AgentsListIsEmptyError
from api.models.analisys.analyze_doc_request import AnalyzeDocRequest
from api.models.analisys.analyze_doc_response import AnalyzeDocResponse
from api.models.analisys.chat_doc_request import ChatDocRequest
from api.models.analisys.chat_doc_response import ChatDocResponse
from api.models.analisys.clarify_doc_request import ClarifyDocRequest
from api.models.analisys.clarify_doc_response import ClarifyDocResponse
from api.models.analisys.history_response import HistoryResponse
from api.models.analisys.result_data import ResultData
from data.app_state_manager import AppStateManager

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
    if len(request.agents) > 1:
        await council.create_council(request.agents)
        result = await council.analyze_doc(
            resources=request.resources, role=request.role
        )

        answers = result["answers"]
        iterations = result["iterations"]
        judgements = result["judgements"]
        scores = result["scores"]

        return AnalyzeDocResponse(
            result=[
                ResultData(answer=answer, judgement=judgement, score=score)
                for answer, judgement, score in zip_longest(
                    answers, judgements, scores, fillvalue=None
                )
            ],
            elapsed=result["elapsed"],
            token_usage=result["token_usage"],
            cost_rub=0,
        )

    if len(request.agents) == 0:
        raise AgentsListIsEmptyError()

    result = await agent.analyze_doc(
        resources=request.resources, role=request.role, model=request.agents[0].model
    )
    return AnalyzeDocResponse(
        result=[ResultData(answer=result["answer"])],
        elapsed=result["elapsed"],
        token_usage=result["token_usage"],
        cost_rub=result["cost_rub"],
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
    app_state: AppStateManager = Depends(get_app_state),
):
    async def generate():
        try:
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
                    if len(request.agents) > 1:
                        await council.create_council(request.agents)
                        result = await council.analyze_doc(
                            resources=request.resources,
                            role=request.role,
                            limit=request.limit,
                            progress_callback=progress_callback,
                        )

                        answers = result["answers"]
                        iterations = result["iterations"]
                        judgements = result["judgements"]
                        scores = result["scores"]

                        await app_state.add_token_usage(result["token_usage"])
                        total_token_usage = await app_state.get_token_usage()
                        logger.info(f"Total token usage: {total_token_usage}")

                        final_result = {
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
                            "elapsed": result["elapsed"],
                            "token_usage": result["token_usage"].model_dump()
                            if result["token_usage"]
                            else None,
                            "total_token_usage": total_token_usage.model_dump(),
                        }
                    elif len(request.agents) == 1:
                        await progress_callback(
                            "agent_start",
                            {
                                "agentId": 1,
                                "agentType": "exec",
                            },
                        )

                        result = await agent.analyze_doc(
                            resources=request.resources,
                            role=request.role,
                            model=request.agents[0].model,
                            limit=request.limit,
                        )

                        await app_state.add_token_usage(result["token_usage"])
                        total_token_usage = await app_state.get_token_usage()
                        logger.info(f"Total token usage: {total_token_usage}")

                        final_result = {
                            "result": [
                                {
                                    "answer": result["answer"],
                                }
                            ],
                            "elapsed": result["elapsed"],
                            "token_usage": result["token_usage"].model_dump()
                            if result["token_usage"]
                            else None,
                            "total_token_usage": total_token_usage.model_dump(),
                        }

                        await progress_callback(
                            "agent_end",
                            {
                                "agentId": 1,
                                "agentType": "exec",
                            },
                        )

                    else:
                        raise AgentsListIsEmptyError()

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

            analysis_task = asyncio.create_task(run_analysis())

            while True:
                event = await event_queue.get()

                sse_message = f"event: {event['event']}\n"
                sse_message += (
                    f"data: {json.dumps(event['data'], ensure_ascii=False)}\n\n"
                )

                yield sse_message

                if event["event"] in ["complete", "error"]:
                    break

            await analysis_task

        except Exception as e:
            logger.error(f"Documents analysis stream error: {e}", exc_info=True)
            yield f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n"

    return StreamingResponse(
        generate(),
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
    app_state: AppStateManager = Depends(get_app_state),
):
    result = await agent.clarify(
        ai_answer=request.ai_answer,
        user_message=request.user_message,
        model=request.model,
    )

    await app_state.add_token_usage(result["token_usage"])
    total_token_usage = await app_state.get_token_usage()
    logger.info(f"Total token usage: {total_token_usage}")

    return ClarifyDocResponse(
        result=ResultData(answer=result["answer"]),
        elapsed=result["elapsed"],
        token_usage=result["token_usage"],
        total_token_usage=total_token_usage,
        cost_rub=result["cost_rub"],
    )


@router.post(
    "/doc/chat", response_model=ChatDocResponse, response_model_exclude_none=True
)
async def api_chat(
    request: ChatDocRequest,
    agent: Agent = Depends(get_agent),
    app_state: AppStateManager = Depends(get_app_state),
):
    result = await agent.chat(user_message=request.user_message, model=request.model)

    await app_state.add_token_usage(result["token_usage"])
    total_token_usage = await app_state.get_token_usage()
    logger.info(f"Total token usage: {total_token_usage}")

    return ChatDocResponse(
        result=ResultData(answer=result["answer"]),
        elapsed=result["elapsed"],
        token_usage=result["token_usage"],
        total_token_usage=total_token_usage,
        cost_rub=result["cost_rub"],
    )


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
    result = await agent.get_history()
    return HistoryResponse(history=result)

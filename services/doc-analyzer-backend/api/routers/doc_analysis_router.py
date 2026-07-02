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
    "/doc/clarify", response_model=ClarifyDocResponse, response_model_exclude_none=True
)
async def api_clarify_doc(
    request: ClarifyDocRequest, agent: Agent = Depends(get_agent)
):
    result = await agent.clarify(
        ai_answer=request.ai_answer,
        user_message=request.user_message,
        model=request.model,
    )
    return ClarifyDocResponse(
        result=ResultData(answer=result["answer"]),
        elapsed=result["elapsed"],
        token_usage=result["token_usage"],
        cost_rub=result["cost_rub"],
    )


@router.post(
    "/doc/chat", response_model=ChatDocResponse, response_model_exclude_none=True
)
async def api_chat(request: ChatDocRequest, agent: Agent = Depends(get_agent)):
    result = await agent.chat(user_message=request.user_message, model=request.model)
    return ChatDocResponse(
        result=ResultData(answer=result["answer"]),
        elapsed=result["elapsed"],
        token_usage=result["token_usage"],
        cost_rub=result["cost_rub"],
    )


@router.post("/doc/chat/stream")
async def api_chat_stream(request: ChatDocRequest, agent: Agent = Depends(get_agent)):
    async def generate():
        try:
            async for chunk in agent.chat_stream(
                user_message=request.user_message, model=request.model
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

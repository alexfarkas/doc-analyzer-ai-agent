import logging

from fastapi import APIRouter, Depends

from src.doc_analyzer_backend.api.dependencies.dependencies import get_user_session
from src.doc_analyzer_backend.api.models.tokens.clear_tokens_response import (
    ClearTokensResponse,
)
from src.doc_analyzer_backend.api.models.tokens.total_tokens_response import (
    TotalTokensResponse,
)
from src.doc_analyzer_backend.session.data.user_session import UserSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/tokens/clear")
async def api_tokens_clear(user: UserSession = Depends(get_user_session)):
    data = user.data
    await data.clear_token_usage()
    await data.clear_cost()
    logger.info("Total token usage is cleared")
    logger.info("Total cost is cleared")
    return ClearTokensResponse(status="success")


@router.get("/tokens/total")
async def api_tokens_total(user: UserSession = Depends(get_user_session)):
    data = user.data
    return TotalTokensResponse(
        total_token_usage=data.get_token_usage(),
        total_cost=data.get_cost(),
    )

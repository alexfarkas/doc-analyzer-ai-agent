import logging

from fastapi import APIRouter, Depends

from src.doc_analyzer_backend.api.dependencies.dependencies import get_app_state, get_user_session
from src.doc_analyzer_backend.api.models.tokens.clear_tokens_response import (
    ClearTokensResponse,
)
from src.doc_analyzer_backend.api.models.tokens.total_tokens_response import (
    TotalTokensResponse,
)
from src.doc_analyzer_backend.data.app_state_manager import AppStateManager
from src.doc_analyzer_backend.session.data.user_session import UserSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/tokens/clear")
async def api_tokens_clear(
    app_state: AppStateManager = Depends(get_app_state),
    user: UserSession = Depends(get_user_session),
):
    await app_state.clear_token_usage()
    await app_state.clear_cost()
    logger.info("Total token usage is cleared")
    logger.info("Total cost is cleared")
    return ClearTokensResponse(status="success")


@router.get("/tokens/total")
async def api_tokens_total(
    app_state: AppStateManager = Depends(get_app_state),
    user: UserSession = Depends(get_user_session),
):
    return TotalTokensResponse(
        total_token_usage=await app_state.get_token_usage(),
        total_cost=await app_state.get_cost(),
    )

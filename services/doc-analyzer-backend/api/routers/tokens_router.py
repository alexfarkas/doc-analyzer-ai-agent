import logging

from fastapi import APIRouter, Depends

from api.dependencies.dependencies import get_app_state
from api.models.tokens.clear_tokens_response import ClearTokensResponse
from api.models.tokens.total_tokens_response import TotalTokensResponse
from data.app_state_manager import AppStateManager

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/tokens/clear")
async def api_tokens_clear(app_state: AppStateManager = Depends(get_app_state)):
    await app_state.clear_token_usage()
    logger.info("Total token usage is cleared")
    return ClearTokensResponse(status="success")


@router.get("/tokens/total")
async def api_tokens_total(app_state: AppStateManager = Depends(get_app_state)):
    total_token_usage = await app_state.get_token_usage()
    return TotalTokensResponse(total_token_usage=total_token_usage)

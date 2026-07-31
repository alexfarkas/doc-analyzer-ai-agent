import logging

from fastapi import APIRouter, Depends

from src.doc_analyzer_backend.api.dependencies.dependencies import get_user_session
from src.doc_analyzer_backend.api.models.user_session.delete_user_session_response import DeleteUserSessionResponse
from src.doc_analyzer_backend.api.models.user_session.get_user_session_response import GetUserSessionResponse
from src.doc_analyzer_backend.session.data.user_session import UserSession

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/sessions/current", response_model=GetUserSessionResponse)
async def api_get_user_session(user: UserSession = Depends(get_user_session)):
    return GetUserSessionResponse(session_id=user.session_id)


@router.delete("/sessions/current", response_model=DeleteUserSessionResponse)
async def api_get_user_session(user: UserSession = Depends(get_user_session)):
    return DeleteUserSessionResponse(
        session_id=user.session_id,
        message="Session deleted",
    )

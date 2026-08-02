import logging
from dataclasses import dataclass

from fastapi import Response, Cookie

from src.doc_analyzer_backend.session.data.user_session import UserSession
from src.doc_analyzer_backend.session.user_manager import user_manager

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class CookieParams:
    key: str
    path: str
    max_age: int


SESSION_COOKIE = CookieParams(
    key="session_id",
    path="/",
    max_age=24 * 3600,
)


def _set_cookie(response: Response, params: CookieParams, value: str):
    response.set_cookie(
        key=params.key,
        value=value,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=params.max_age,
        path=params.path,
    )


async def get_user_session(
    response: Response,
    session_id: str | None = Cookie(None, alias="session_id"),
) -> UserSession:
    logger.info(f"Getting user session id: {session_id}")
    if session_id:
        session = user_manager.get_session(session_id=session_id)
        if session:
            logger.info("Using existing user session")
            return session
    logger.info(f"Creating user session")
    session = await user_manager.create_session()
    _set_cookie(response=response, params=SESSION_COOKIE, value=session.session_id)
    logger.info(f"New user session created with session_id: {session.session_id}")
    return session

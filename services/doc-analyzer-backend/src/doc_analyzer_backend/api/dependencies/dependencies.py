import logging

from fastapi import Request, Response, Cookie

from src.doc_analyzer_backend.api.cookie.cookie_manager import set_session_cookie
from src.doc_analyzer_backend.session.data.user_session import UserSession
from src.doc_analyzer_backend.session.user_manager import user_manager

logger = logging.getLogger(__name__)


async def get_user_session(
    request: Request,
    response: Response,
    session_id: str | None = Cookie(None, alias="session_id"),
) -> UserSession:
    logger.debug(f"== COOKIE DEBUG ==")
    logger.debug(f"Request URL: {request.url}")
    logger.debug(f"Request Host: {request.headers.get('host')}")
    logger.debug(f"All cookies: {dict(request.cookies)}")
    logger.debug(f"Cookie header: {request.headers.get('cookie')}")
    logger.debug(f"Session ID from param: {session_id}")
    logger.debug(f"=================")

    logger.info(f"Getting user session id: {session_id}")
    if session_id:
        session = user_manager.get_session(session_id=session_id)
        if session:
            logger.info("Using existing user session")
            return session
    logger.info(f"Creating user session")
    session = await user_manager.create_session()
    set_session_cookie(response=response, value=session.session_id)
    logger.info(f"New user session created with session_id: {session.session_id}")
    return session

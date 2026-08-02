from dataclasses import dataclass

from fastapi import Request, Response, Cookie

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.council.council import Council
from src.doc_analyzer_backend.data.app_state_manager import AppStateManager, app_state
from src.doc_analyzer_backend.session.data.user_session import UserSession
from src.doc_analyzer_backend.session.user_manager import user_manager


def get_agent(request: Request) -> Agent:
    return request.app.state.agent


def get_council(request: Request) -> Council:
    return request.app.state.council


def get_app_state() -> AppStateManager:
    return app_state


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


def get_user_session(
    response: Response,
    session_id: str | None = Cookie(None, alias="session_id"),
) -> UserSession:
    if session_id:
        session = user_manager.get_session(session_id=session_id)
        if session:
            return session
    session = user_manager.create_session()
    _set_cookie(response=response, params=SESSION_COOKIE, value=session_id)
    return session

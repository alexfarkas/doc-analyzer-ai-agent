from fastapi import Request

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.council.council import Council
from src.doc_analyzer_backend.data.app_state_manager import AppStateManager, app_state


def get_agent(request: Request) -> Agent:
    return request.app.state.agent


def get_council(request: Request) -> Council:
    return request.app.state.council


def get_app_state() -> AppStateManager:
    return app_state

from fastapi import Request

from agent.agent import Agent
from agent.council.council import Council
from data.app_state_manager import AppStateManager, app_state


def get_agent(request: Request) -> Agent:
    return request.app.state.agent


def get_council(request: Request) -> Council:
    return request.app.state.council


def get_app_state() -> AppStateManager:
    return app_state

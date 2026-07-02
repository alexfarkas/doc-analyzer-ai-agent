from fastapi import Request

from agent.agent import Agent
from agent.council.council import Council


def get_agent(request: Request) -> Agent:
    return request.app.state.agent


def get_council(request: Request) -> Council:
    return request.app.state.council

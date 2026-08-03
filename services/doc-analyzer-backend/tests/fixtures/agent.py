from unittest.mock import AsyncMock, MagicMock, Mock

import pytest

from src.doc_analyzer_backend.agent.agent import Agent
from src.doc_analyzer_backend.agent.council.council import Council
from src.doc_analyzer_backend.agent.models.analysis.agent_analysis_data import (
    AgentAnalysisData,
)
from tests.consts.answers import DEFAULT_CLARIFY_ANSWER, DEFAULT_CHAT_ANSWER
from tests.consts.prompts import DEFAULT_HISTORY_SYSTEM_PROMPT
from tests.factories.agent import make_agent_analyze_doc, make_council_analyze_doc
from tests.factories.answers import make_answer_item
from tests.factories.tokens import make_token_usage, make_consumption_data


@pytest.fixture
def mock_agent():
    """Agent mock"""
    agent = AsyncMock(spec=Agent)

    agent.tools = []
    agent._history = MagicMock()
    agent._history.system_prompt = DEFAULT_HISTORY_SYSTEM_PROMPT
    agent._history.as_string = Mock(return_value="")

    agent.analyze_doc = AsyncMock(return_value=make_agent_analyze_doc())
    agent.clarify = AsyncMock(
        return_value=AgentAnalysisData(
            answer_item=make_answer_item(DEFAULT_CLARIFY_ANSWER),
            consumption_data=make_consumption_data(),
        )
    )
    agent.chat = AsyncMock(
        return_value=AgentAnalysisData(
            answer_item=make_answer_item(DEFAULT_CHAT_ANSWER),
            consumption_data=make_consumption_data(),
        )
    )

    async def mock_chat_stream(*args, **kwargs):
        yield "Сообщение 1"
        yield "Сообщение 2"
        yield '\n__METADATA__:{"token_usage": {"input_tokens": 10, "output_tokens": 5, "total_tokens": 15}}'

    agent.chat_stream = mock_chat_stream
    agent.get_history = AsyncMock(return_value="История")
    return agent


@pytest.fixture
def failing_mock_agent(mock_agent):
    """Agent mock that raises exception"""
    original = mock_agent.analyze_doc.side_effect
    mock_agent.analyze_doc.side_effect = Exception("Agent error")
    yield mock_agent
    mock_agent.analyze_doc.side_effect = original


@pytest.fixture
def mock_council():
    """Council mock"""
    council = AsyncMock(spec=Council)
    council.create_council = AsyncMock(return_value=None)
    council.analyze_doc = AsyncMock(return_value=make_council_analyze_doc())
    return council

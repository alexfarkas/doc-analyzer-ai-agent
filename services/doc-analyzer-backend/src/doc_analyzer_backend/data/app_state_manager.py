import asyncio
import logging

from src.doc_analyzer_backend.api.models.analisys import answer_seq
from src.doc_analyzer_backend.api.models.analisys.answer_item import AnswerItem
from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq
from src.doc_analyzer_backend.data.app_data import AppData
from src.doc_analyzer_backend.agent.models.tokens.token_usage import (
    TokenUsage,
    create_token_usage,
)

logger = logging.getLogger(__name__)


class AppStateManager:
    def __init__(self):
        self._data = AppData()
        self._lock = asyncio.Lock()

    async def get_answer_seqs(self):
        return self._data.answer_seqs

    async def get_answer_seq(self, agent_index: int) -> AnswerSeq:
        idx = agent_index - 1
        if len(self._data.answer_seqs) <= idx:
            logger.warning(f"Requested answer seq does not exist at index {idx} (agent index {agent_index}) "
                           f"as total answer seqs length is {len(self._data.answer_seqs)}")
            raise Exception(f"Requested answer seq does not exist at index {idx}")
        return self._data.answer_seqs[idx]

    async def set_answer_seqs(
        self,
        answer_item: AnswerItem | None = None,
        answer_seqs: list[AnswerSeq] | None = None,
    ):
        if answer_item:
            async with self._lock:
                self._data.answer_seqs = [AnswerSeq(answers=[answer_item])]
        elif answer_seqs:
            async with self._lock:
                self._data.answer_seqs = answer_seqs

    async def clear_answer_seqs(self):
        async with self._lock:
            self._data.answer_seqs = []

    async def get_token_usage(self) -> TokenUsage:
        return self._data.token_usage

    async def set_token_usage(self, token_usage: TokenUsage):
        async with self._lock:
            self._data.token_usage = token_usage

    async def add_token_usage(self, token_usage: TokenUsage | None):
        if token_usage:
            async with self._lock:
                self._data.token_usage.add_usage(token_usage)

    async def clear_token_usage(self):
        async with self._lock:
            self._data.token_usage = create_token_usage()

    async def get_cost(self) -> float:
        return self._data.cost

    async def set_cost(self, cost: float):
        async with self._lock:
            self._data.cost = cost

    async def add_cost(self, cost: float = 0.0):
        async with self._lock:
            self._data.cost += cost

    async def clear_cost(self):
        async with self._lock:
            self._data.cost = 0.0


app_state = AppStateManager()

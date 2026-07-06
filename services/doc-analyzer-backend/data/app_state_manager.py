import asyncio

from data.app_data import AppData
from llm.tokens.token_usage import TokenUsage, create_token_usage


class AppStateManager:
    def __init__(self):
        self._data = AppData()
        self._lock = asyncio.Lock()

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


app_state = AppStateManager()

from typing import Iterator, Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration


class LLMMock(BaseChatModel):
    fixed_response: str = "default llm mock response"
    model_name: str = "mock"

    @property
    def _llm_type(self) -> str:
        return "mock_llm"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any | None = None,
        **kwargs: Any,
    ) -> ChatResult:
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=self.fixed_response))]
        )

    async def _agenerate(self, *args: Any, **kwargs: Any) -> ChatResult:
        return self._generate(*args, **kwargs)

    def _stream(self, *args: Any, **kwargs: Any) -> Iterator[ChatGeneration]:
        yield ChatGeneration(message=AIMessage(content=self.fixed_response))

    async def _astream(self, *args: Any, **kwargs: Any) -> Any:
        for chunk in self._stream(*args, **kwargs):
            yield chunk

    def bind_tools(self, tool, *, tool_choice=None, **kwargs):
        return self

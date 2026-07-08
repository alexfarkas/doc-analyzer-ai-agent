import logging

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool

from src.doc_analyzer_backend.config.llm_config import LLMConfig
from src.doc_analyzer_backend.config.provider_config import provider_config
from src.doc_analyzer_backend.llm.llm_factory import LLMFactory

logger = logging.getLogger(__name__)


class LLMModelManager:
    def __init__(
        self,
        llm_config: LLMConfig,
        tools: list[BaseTool],
    ):
        self._llm_config = llm_config
        self._provider = llm_config.provider
        self._model = llm_config.model
        self._tools = tools

    @property
    def current_model(self) -> str:
        return self._model

    def model_is_new(self, new_model: str | None) -> bool:
        if not new_model:
            return False

        new_provider = provider_config.get_provider_by_model(new_model)
        return self._provider != new_provider or self._model != new_model

    async def setup_model(self, new_model: str | None) -> BaseChatModel | None:
        if new_model is None:
            return None

        new_provider = provider_config.get_provider_by_model(new_model)

        try:
            logger.info(
                f"Changing LLM model from {self._provider}/{self._model} to {new_provider}/{new_model}..."
            )

            new_llm = LLMFactory.create_llm(self._llm_config, new_provider, new_model)
            new_llm = new_llm.bind_tools(self._tools)

            self._provider = new_provider
            self._model = new_model

            logger.info(f"LLM model changed to {new_provider}/{new_model}")

            return new_llm
        except Exception as e:
            logger.error(f"Error while changing LLM model: {e}")
            return None

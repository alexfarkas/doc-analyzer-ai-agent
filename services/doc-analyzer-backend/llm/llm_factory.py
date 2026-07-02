from langchain_core.language_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from config.llm_config import LLMConfig
from llm.llm_mock import LLMMock


class LLMFactory:
    @staticmethod
    def create_llm(
        llm_config: LLMConfig,
        new_provider: str | None = None,
        new_model: str | None = None,
    ) -> BaseChatModel:
        provider = new_provider or llm_config.provider
        model = new_model or llm_config.model
        match provider:
            case "mock":
                return LLMMock(fixed_response=llm_config.mock_response)
            case "ollama":
                return ChatOllama(model=model, base_url=llm_config.base_url)
            case "openai":
                return ChatOpenAI(
                    model=f"{provider}/{model}",
                    base_url=llm_config.base_url,
                    api_key=llm_config.api_key,
                    timeout=300.0,
                    max_retries=3,
                )
            case _:
                raise ValueError(f"Unknown provider: {provider}")

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings


class LLMConfig(BaseSettings):
    provider: str = Field(default="openai", description="LLM provider")
    model: str = Field(default="gpt-5-nano", description="LLM model")
    base_url: str | None = Field(default=None, description="LLM base url")
    api_key: SecretStr | None = Field(
        default=None, description="LLM API key", exclude=True
    )
    temperature: float = Field(
        default=1.0, ge=0.0, le=2.0, description="LLM generation temperature"
    )

    cost_calculation_provider: str | None = Field(
        default=None, description="LLM provider for cost calculation"
    )
    mock_response: str = Field(
        default="Произведен анализ загруженного документа",
        description="LLM mock response",
    )

    model_config = {
        "env_file": ".env",
        "env_prefix": "LLM_",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


llm_config = LLMConfig()

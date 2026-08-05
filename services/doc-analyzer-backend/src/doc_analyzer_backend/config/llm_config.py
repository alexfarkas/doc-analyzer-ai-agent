from pydantic import Field, SecretStr, BaseModel


class LLMConfig(BaseModel):
    provider: str = Field(description="LLM provider")
    model: str = Field(description="LLM model")
    base_url: str | None = Field(default=None, description="LLM base url")
    api_key: SecretStr | None = Field(
        default=None, description="LLM API key", exclude=True
    )
    temperature: float = Field(default=1.0, ge=0.0, le=2.0, description="LLM generation temperature")

    cost_calculation_provider: str | None = Field(
        default=None, description="LLM provider for cost calculation"
    )
    mock_response: str = Field(
        default="Произведен анализ загруженного документа",
        description="LLM mock response",
    )

from pydantic import Field
from pydantic_settings import BaseSettings


class ProviderConfig(BaseSettings):
    providers_models: dict[str, list[str]] = Field(
        default_factory=dict, description="Providers and models mapping"
    )

    def get_provider_by_model(self, model: str) -> str | None:
        for provider, models in self.providers_models.items():
            if model.lower() in [m.lower() for m in models]:
                return provider
        return None

    model_config = {
        "env_file": ".env",
        "env_prefix": "PVDR_",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


provider_config = ProviderConfig()

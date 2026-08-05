from pydantic import Field, BaseModel


class ProviderConfig(BaseModel):
    providers_models: dict[str, list[str]] = Field(
        default_factory=dict, description="Providers and models mapping"
    )

    def get_provider_by_model(self, model: str) -> str | None:
        for provider, models in self.providers_models.items():
            if model.lower() in [m.lower() for m in models]:
                return provider
        return None

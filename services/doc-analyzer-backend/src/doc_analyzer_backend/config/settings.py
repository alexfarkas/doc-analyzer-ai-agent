import logging

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from src.doc_analyzer_backend.config.app_config import app_config
from src.doc_analyzer_backend.config.pricing_config import PricingConfig
from src.doc_analyzer_backend.config.sources import FileConfigSettingsSource

logger = logging.getLogger(__name__)


class AppSettings(BaseSettings):
    pricing: PricingConfig = Field(default_factory=PricingConfig)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="APP_",
        case_sensitive=False,
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls,
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        """
        Настраивает порядок и состав источников настроек.

        Порядок (слева направо = от низкого к высокому приоритету):
        1. Значения из __init__()
        2. pricing.json (базовые цены)
        3. llm.yaml (базовые настройки LLM)
        4. Системные переменные окружения
        5. .env файл (самый высокий приоритет)
        """
        pricing_filepath = app_config.pricing_filepath
        if not pricing_filepath:
            logger.warning(f"Pricing config filepath not found in '{pricing_filepath}'.")
            pricing_filepath = ""

        return (
            init_settings,
            FileConfigSettingsSource(settings_cls, pricing_filepath),
            env_settings,
            # dotenv_settings,
        )


_settings: AppSettings | None = None


def app_settings() -> AppSettings:
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings

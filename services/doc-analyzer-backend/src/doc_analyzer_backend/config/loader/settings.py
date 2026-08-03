import logging
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from src.doc_analyzer_backend.config.app_config import app_config
from src.doc_analyzer_backend.config.pricing_config import PricingConfig
from src.doc_analyzer_backend.config.loader.sources import FileConfigSettingsSource

logger = logging.getLogger(__name__)

CONFIG_DIR = "config"


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
        2. yaml файлы
        3. Системные переменные окружения
        4. .env файл (самый высокий приоритет)
        """
        project_root_dir: Path = Path(__file__).resolve().parents[4]

        filepath_pricing = cls._get_config_path(project_root_dir=project_root_dir, filename="pricing.yaml")

        return (
            init_settings,
            FileConfigSettingsSource(settings_cls, filepath_pricing),
            #env_settings,
            # dotenv_settings,
        )

    @classmethod
    def _get_config_path(cls, project_root_dir: Path, filename: str) -> str:
        filepath = os.path.join(project_root_dir, CONFIG_DIR, filename)
        if not os.path.isfile(filepath):
            logger.error(f"Config filepath not found in '{filepath}'.")
            raise FileNotFoundError(f"Config filepath not found in '{filepath}'.")
        return filepath


_settings: AppSettings | None = None


def app_settings() -> AppSettings:
    global _settings
    if _settings is None:
        _settings = AppSettings()
    return _settings

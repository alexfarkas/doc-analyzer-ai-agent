import logging
import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from src.doc_analyzer_backend.config.app_config import AppConfig
from src.doc_analyzer_backend.config.db_config import DBConfig
from src.doc_analyzer_backend.config.llm_config import LLMConfig
from src.doc_analyzer_backend.config.loader.aggregated_source import AggregatedConfigSource
from src.doc_analyzer_backend.config.logger_config import LoggerConfig
from src.doc_analyzer_backend.config.pricing_config import PricingConfig
from src.doc_analyzer_backend.config.provider_config import ProviderConfig
from src.doc_analyzer_backend.config.rag_config import RAGConfig
from src.doc_analyzer_backend.config.service_config import ServiceConfig

logger = logging.getLogger(__name__)

CONFIG_DIR = "config"


class AppSettings(BaseSettings):
    app: AppConfig = Field(default_factory=AppConfig)
    service: ServiceConfig = Field(default_factory=ServiceConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    provider: ProviderConfig = Field(default_factory=ProviderConfig)
    db: DBConfig = Field(default_factory=DBConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    logger: LoggerConfig = Field(default_factory=LoggerConfig)
    pricing: PricingConfig = Field(default_factory=PricingConfig)

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="ignore",
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

        filepath_app = cls._get_config_path(project_root_dir=project_root_dir, filename="app.yaml")
        filepath_service = cls._get_config_path(project_root_dir=project_root_dir, filename="service.yaml")
        filepath_llm = cls._get_config_path(project_root_dir=project_root_dir, filename="llm.yaml")
        filepath_provider = cls._get_config_path(project_root_dir=project_root_dir, filename="provider.yaml")
        filepath_db = cls._get_config_path(project_root_dir=project_root_dir, filename="db.yaml")
        filepath_rag = cls._get_config_path(project_root_dir=project_root_dir, filename="rag.yaml")
        filepath_logger = cls._get_config_path(project_root_dir=project_root_dir, filename="logger.yaml")
        filepath_pricing = cls._get_config_path(project_root_dir=project_root_dir, filename="pricing.yaml")

        return (
            init_settings,
            AggregatedConfigSource(
                settings_cls=settings_cls,
                yaml_paths=[
                    filepath_app,
                    filepath_service,
                    filepath_llm,
                    filepath_provider,
                    filepath_db,
                    filepath_rag,
                    filepath_logger,
                    filepath_pricing,
                ],
                env_file=".env",
            ),
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

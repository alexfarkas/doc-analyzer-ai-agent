from pathlib import Path

from pydantic import Field, BaseModel, field_validator

from src.doc_analyzer_backend.config.loader.paths import PROJECT_ROOT


class DBConfig(BaseModel):
    url: str = Field(description="Database connection URL")
    use_db_prompts: bool = Field(description="Use database prompts instead of local")

    @field_validator("url", mode="before")
    @classmethod
    def resolve_sqlite_path(cls, value: str) -> str:
        """Преобразует относительный путь в SQLite URL."""
        if not value or not value.startswith("sqlite:///"):
            return value
        db_path = value[len("sqlite:///"):]
        path = Path(db_path)
        if path.is_absolute():
            return value
        absolute_path = (PROJECT_ROOT / path).resolve()
        return f"sqlite:///{absolute_path}"

from pydantic import Field
from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    allowed_exts: list[str] = Field(
        default=[
            ".txt",
            ".md",
            ".csv",
            ".json",
            ".yaml",
            ".yml",
            ".html",
            ".xml",
            ".docx",
            ".xlsx",
            ".pptx",
            ".pdf",
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".tiff",
            ".bmp",
            ".py",
            ".js",
            ".ts",
            ".java",
            ".kt",
            ".scala",
            ".cs",
            ".cpp",
            ".go",
            ".php",
            ".swift",
            ".r",
            ".pl",
            ".sql",
            ".sh",
            ".zsh",
            ".bash",
        ],
        description="List of allowed file extensions",
    )

    docs_dir: str = Field(
        default="./documents", description="Documents upload and analysis folder"
    )

    pricing_filepath: str = Field(
        default="./documents", description="Documents upload and analysis folder"
    )

    max_file_preview_size: int = Field(
        default=1024 * 1024, description="Max file preview size in bytes"
    )

    model_config = {
        "env_file": ".env",
        "env_prefix": "APP_",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


app_config = AppConfig()

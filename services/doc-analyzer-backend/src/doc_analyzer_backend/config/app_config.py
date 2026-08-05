from pydantic import Field, BaseModel


class AppConfig(BaseModel):
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

    max_file_preview_size: int = Field(
        default=1024 * 1024, description="Max file preview size in bytes"
    )

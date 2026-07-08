from pydantic import Field
from pydantic_settings import BaseSettings


class LoggerConfig(BaseSettings):
    path: str = Field(default="./logs/backend.log", description="Log path")
    level: str = Field(default="INFO", description="Log level")
    write_to_file: bool = Field(default=False, description="Write logs to file")

    model_config = {
        "env_file": ".env",
        "env_prefix": "LOG_",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


logger_config = LoggerConfig()

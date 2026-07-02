from pydantic import Field
from pydantic_settings import BaseSettings


class DBConfig(BaseSettings):
    url: str = Field(
        default="sqlite:///./data/prompts.db", description="Database connection URL"
    )
    use_db_prompts: bool = Field(
        default=False, description="Use database prompts instead of local"
    )

    model_config = {
        "env_file": ".env",
        "env_prefix": "DB_",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


db_config = DBConfig()

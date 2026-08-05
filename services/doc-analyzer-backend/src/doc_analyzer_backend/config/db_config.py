from pydantic import Field, BaseModel


class DBConfig(BaseModel):
    url: str = Field(description="Database connection URL")
    use_db_prompts: bool = Field(description="Use database prompts instead of local")

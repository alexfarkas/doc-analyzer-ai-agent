from pydantic import Field, BaseModel


class LoggerConfig(BaseModel):
    path: str = Field(description="Log path")
    level: str = Field(description="Log level")
    write_to_file: bool = Field(description="Write logs to file")

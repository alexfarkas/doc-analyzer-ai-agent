from pydantic import BaseModel, Field


class ServiceConfig(BaseModel):
    host: str = Field(default="127.0.0.1", description="API service IP address")
    port: int = Field(default=8000, description="API service port")
    timeout_keep_alive: int = Field(
        default=300, description="API service keep alive timeout"
    )
    timeout_graceful_shutdown: int = Field(
        default=300, description="API service graceful shutdown timeout"
    )
    reload: bool = Field(default=True, description="API service auto reload")

    model_config = {
        "env_file": ".env",
        "env_prefix": "SVC_",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


service_config = ServiceConfig()

from pydantic import BaseModel, Field, field_validator, HttpUrl


class UploadFromUrlRequest(BaseModel):
    url: HttpUrl = Field(..., description="Resources upload URL")

    @field_validator("url")
    @classmethod
    def validate_url_scheme(cls, v: HttpUrl) -> str:
        return str(v)

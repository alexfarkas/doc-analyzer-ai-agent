from pydantic import BaseModel, Field


class UploadFromUrlResponse(BaseModel):
    url: str = Field(..., description="Resources upload URL")
    html: str = Field(..., description="Resources uploaded HTML")

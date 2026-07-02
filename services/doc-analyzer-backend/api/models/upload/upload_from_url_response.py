from pydantic import BaseModel


class UploadFromUrlResponse(BaseModel):
    html: str
    url: str

from pydantic import BaseModel


class UploadFromUrlRequest(BaseModel):
    url: str

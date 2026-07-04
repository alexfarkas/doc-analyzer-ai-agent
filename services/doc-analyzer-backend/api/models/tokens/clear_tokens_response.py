from pydantic import BaseModel


class ClearTokensResponse(BaseModel):
    status: str

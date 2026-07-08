from pydantic import BaseModel


class ModelData(BaseModel):
    provider: str
    name: str

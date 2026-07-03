from pydantic import BaseModel


class ResultIterData(BaseModel):
    answer: str

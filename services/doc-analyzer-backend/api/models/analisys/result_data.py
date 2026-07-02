from pydantic import BaseModel


class ResultData(BaseModel):
    answer: str
    score: int | None = None
    judgement: str | None = None

from pydantic import BaseModel

from api.models.analisys.result_iter_data import ResultIterData


class ResultData(BaseModel):
    answer: str
    score: int | None = None
    judgement: str | None = None
    answer_iterations: list[ResultIterData] = None

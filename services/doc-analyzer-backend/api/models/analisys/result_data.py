from pydantic import BaseModel

from api.models.analisys.answer_seq import AnswerSeq


class ResultData(BaseModel):
    answer_seq: AnswerSeq
    score: float | None = None
    judgement: str | None = None

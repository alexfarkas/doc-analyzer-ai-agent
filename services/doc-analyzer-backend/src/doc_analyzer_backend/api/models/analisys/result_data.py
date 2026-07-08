from pydantic import BaseModel

from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq


class ResultData(BaseModel):
    answer_seq: AnswerSeq
    score: float | None = None
    judgement: str | None = None

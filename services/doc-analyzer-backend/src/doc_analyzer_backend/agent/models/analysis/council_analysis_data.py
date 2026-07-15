from pydantic import BaseModel

from src.doc_analyzer_backend.agent.models.tokens.consumption_data import (
    ConsumptionData,
)
from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq


class CouncilAnalysisData(BaseModel):
    answer_seqs: list[AnswerSeq]
    judgements: list[str]
    scores: list[float | None]
    consumption_data: ConsumptionData

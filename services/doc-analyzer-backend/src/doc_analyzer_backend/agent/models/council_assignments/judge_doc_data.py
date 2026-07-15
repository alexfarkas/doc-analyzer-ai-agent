from pydantic import BaseModel

from src.doc_analyzer_backend.agent.models.tokens.consumption_data import (
    ConsumptionData,
)


class JudgeDocData(BaseModel):
    answer_judgements: list[str]
    answer_score: float
    success_count: int
    failed_count: int
    consumption_data: ConsumptionData

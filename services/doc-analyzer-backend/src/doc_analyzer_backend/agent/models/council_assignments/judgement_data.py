from pydantic import BaseModel

from src.doc_analyzer_backend.agent.models.tokens.consumption_data import ConsumptionData


class JudgementData(BaseModel):
    judgements: list[str]
    scores: list[float]
    consumption_data: ConsumptionData

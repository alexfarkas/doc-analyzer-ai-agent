from pydantic import BaseModel

from src.doc_analyzer_backend.agent.models.tokens.consumption_data import ConsumptionData
from src.doc_analyzer_backend.agent.models.tokens.token_usage import TokenUsage


class ChatMetadata(BaseModel):
    consumption_data: ConsumptionData
    total_token_usage: TokenUsage | None
    total_cost: float = 0.0

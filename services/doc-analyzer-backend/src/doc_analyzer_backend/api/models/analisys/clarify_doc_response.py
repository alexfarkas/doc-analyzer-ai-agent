from pydantic import BaseModel

from src.doc_analyzer_backend.api.models.analisys.result_data import ResultData
from src.doc_analyzer_backend.agent.models.tokens.token_usage import TokenUsage


class ClarifyDocResponse(BaseModel):
    result: ResultData
    token_usage: TokenUsage
    total_token_usage: TokenUsage
    elapsed: float
    cost: float
    total_cost: float
    currency: str = "RUB"

from pydantic import BaseModel

from src.doc_analyzer_backend.agent.models.tokens.token_usage import TokenUsage


class TotalTokensResponse(BaseModel):
    total_token_usage: TokenUsage
    total_cost: float

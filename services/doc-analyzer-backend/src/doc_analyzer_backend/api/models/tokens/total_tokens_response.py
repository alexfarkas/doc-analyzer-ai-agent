from pydantic import BaseModel

from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage


class TotalTokensResponse(BaseModel):
    total_token_usage: TokenUsage

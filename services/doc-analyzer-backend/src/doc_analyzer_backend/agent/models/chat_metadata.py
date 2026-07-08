from pydantic import BaseModel

from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage


class ChatMetadata(BaseModel):
    token_usage: TokenUsage | None
    total_token_usage: TokenUsage | None
    elapsed: float
    cost_rub: float = 0

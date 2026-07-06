from pydantic import BaseModel

from llm.tokens.token_usage import TokenUsage


class ChatMetadata(BaseModel):
    token_usage: TokenUsage | None
    total_token_usage: TokenUsage | None
    elapsed: float
    cost_rub: float = 0

from pydantic import BaseModel

from llm.tokens.token_usage import TokenUsage


class TotalTokensResponse(BaseModel):
    total_token_usage: TokenUsage

from pydantic import BaseModel

from llm.tokens.token_usage import TokenUsage


class JudgementData(BaseModel):
    judgements: list[str]
    scores: list[float]
    token_usage: TokenUsage | None = None
    elapsed: float

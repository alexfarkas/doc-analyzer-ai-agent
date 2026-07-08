from pydantic import BaseModel

from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage


class JudgementData(BaseModel):
    judgements: list[str]
    scores: list[float]
    token_usage: TokenUsage | None = None
    elapsed: float

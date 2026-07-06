from pydantic import BaseModel

from api.models.analisys.answer_seq import AnswerSeq
from llm.tokens.token_usage import TokenUsage


class CouncilAnalysisData(BaseModel):
    answer_seqs: list[AnswerSeq]
    judgements: list[str]
    scores: list[float | None]
    token_usage: TokenUsage | None = None
    elapsed: float

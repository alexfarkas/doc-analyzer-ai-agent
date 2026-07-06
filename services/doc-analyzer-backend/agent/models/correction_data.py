from pydantic import BaseModel

from api.models.analisys.answer_seq import AnswerSeq
from llm.tokens.token_usage import TokenUsage


class CorrectionData(BaseModel):
    answer_seqs: list[AnswerSeq]
    token_usage: TokenUsage | None = None
    elapsed: float

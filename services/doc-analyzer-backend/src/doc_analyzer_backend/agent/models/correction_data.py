from pydantic import BaseModel

from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq
from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage


class CorrectionData(BaseModel):
    answer_seqs: list[AnswerSeq]
    token_usage: TokenUsage | None = None
    elapsed: float

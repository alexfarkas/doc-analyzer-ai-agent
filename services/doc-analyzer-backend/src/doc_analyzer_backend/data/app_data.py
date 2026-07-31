from pydantic import BaseModel

from src.doc_analyzer_backend.agent.models.tokens.token_usage import (
    TokenUsage,
    create_token_usage,
)
from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq


class AppData(BaseModel):
    answer_seqs: list[AnswerSeq] = []
    token_usage: TokenUsage = create_token_usage()
    cost: float = 0.0

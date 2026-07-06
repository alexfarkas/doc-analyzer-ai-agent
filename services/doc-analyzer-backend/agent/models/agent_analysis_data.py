from pydantic import BaseModel

from api.models.analisys.answer_seq import AnswerSeq
from llm.tokens.token_usage import TokenUsage


class AgentAnalysisData(BaseModel):
    answer_seq: AnswerSeq
    token_usage: TokenUsage | None = None
    elapsed: float
    cost_rub: float = 0

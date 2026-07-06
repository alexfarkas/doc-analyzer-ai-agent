from pydantic import BaseModel

from api.models.analisys.result_data import ResultData
from llm.tokens.token_usage import TokenUsage


class ChatDocResponse(BaseModel):
    result: ResultData
    token_usage: TokenUsage
    total_token_usage: TokenUsage
    elapsed: float
    cost_rub: float

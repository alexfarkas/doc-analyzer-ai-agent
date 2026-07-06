from pydantic import BaseModel

from llm.tokens.token_usage import TokenUsage, create_token_usage


class AppData(BaseModel):
    token_usage: TokenUsage = create_token_usage()

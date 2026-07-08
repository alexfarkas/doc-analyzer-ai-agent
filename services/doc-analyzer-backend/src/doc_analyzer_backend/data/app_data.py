from pydantic import BaseModel

from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage, create_token_usage


class AppData(BaseModel):
    token_usage: TokenUsage = create_token_usage()

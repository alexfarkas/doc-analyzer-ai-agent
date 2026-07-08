from pydantic import Field
from pydantic_settings import BaseSettings


class RAGConfig(BaseSettings):
    embedding_provider: str = Field(
        default="openai", description="RAG embedding provider"
    )
    embedding_model: str = Field(
        default="text-embedding-3-small", description="RAG embedding model"
    )
    base_url: str | None = Field(
        default=None, description="RAG embedding model base url"
    )
    api_key: str | None = Field(
        default=None, description="RAG embedding model API key", exclude=True
    )
    collection: str | None = Field(default="agent-rag", description="RAG collection")
    top_k: int = Field(default=3, description="Number of RAG documents to retrieve")
    similarity_threshold: float = Field(
        default=0.5, description="Min RAG similarity score"
    )
    max_context_length: int = Field(
        default=2000, ge=500, le=10000, description="Max RAG context length"
    )
    context_block_length: int = Field(
        default=400, description="RAG context block length"
    )
    host: str = Field(default="localhost", description="RAG host")
    port: int = Field(default=8000, description="RAG port")
    path: str = Field(default="./chromedb", description="RAG storage path")
    use_vector_db: bool = Field(default=False, description="Use RAG vector database")
    use_local_vector_db: bool = Field(
        default=True, description="Use local RAG vector database"
    )

    model_config = {
        "env_file": ".env",
        "env_prefix": "RAG_",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore",
    }


rag_config = RAGConfig()

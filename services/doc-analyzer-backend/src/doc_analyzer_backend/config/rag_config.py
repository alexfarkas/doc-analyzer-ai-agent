from pydantic import Field, SecretStr, BaseModel


class RAGConfig(BaseModel):
    embedding_provider: str = Field(description="RAG embedding provider")
    embedding_model: str = Field(description="RAG embedding model")
    base_url: str | None = Field(description="RAG embedding model base url")
    api_key: SecretStr | None = Field(
        default=None, description="RAG embedding model API key", exclude=True
    )
    collection: str | None = Field(description="RAG collection")
    top_k: int = Field(description="Number of RAG documents to retrieve")
    similarity_threshold: float = Field(description="Min RAG similarity score")
    max_context_length: int = Field(ge=500, le=10000, description="Max RAG context length")
    context_block_length: int = Field(description="RAG context block length")
    host: str = Field(default="localhost", description="RAG host")
    port: int = Field(default=8000, description="RAG port")
    path: str = Field(description="RAG storage path")
    use_vector_db: bool = Field(default=False, description="Use RAG vector database")
    use_local_vector_db: bool = Field(
        default=True, description="Use local RAG vector database"
    )

from typing import Protocol, runtime_checkable


@runtime_checkable
class RAGConfigProtocol(Protocol):
    embedding_provider: str
    embedding_model: str
    base_url: str | None
    api_key: str | None
    collection: str | None
    top_k: int
    similarity_threshold: float
    max_context_length: int
    context_block_length: int
    host: str
    port: int
    path: str
    use_vector_db: bool
    use_local_vector_db: bool

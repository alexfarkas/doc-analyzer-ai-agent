"""
rag-client - клиент для RAG

Содержит:
- ChromaDBClient
- ChromaDBClientFactory
- LocalEmbedder
- OpenAIEmbedder
- RAGConfigProtocol
"""

from rag_client.config import RAGConfigProtocol
from rag_client.local_embedder import LocalEmbedder
from rag_client.openai_embedder import OpenAIEmbedder
from rag_client.chromadb_client import ChromaDBClient
from rag_client.chromadb_client_factory import ChromaDBClientFactory

__version__ = "1.0.0"

__all__ = [
    "RAGConfigProtocol",
    "LocalEmbedder",
    "OpenAIEmbedder",
    "ChromaDBClient",
    "ChromaDBClientFactory",
]

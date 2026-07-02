import logging
from pathlib import Path

import chromadb
from chromadb import ClientAPI, Settings
from chromadb.api.models.Collection import Collection

from rag_client import RAGConfigProtocol, LocalEmbedder, OpenAIEmbedder, ChromaDBClient

logger = logging.getLogger(__name__)


class ChromaDBClientFactory:
    def __init__(self, rag_config: RAGConfigProtocol):
        self.rag_config = rag_config

        logger.info("Initializing ChromaDB client factory...")
        self.client = self._create_client()
        self.embedder = self._create_embedder()

        logger.info(
            "ChromaDB client factory initialized: "
            f"provider={rag_config.embedding_provider},"
            f"model={rag_config.embedding_model}, "
            f"dimension={self.embedder.dimension}"
        )

    def _create_client(self) -> ClientAPI:
        if self.rag_config.use_local_vector_db:
            rag_path = Path(self.rag_config.path)
            rag_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using local vector database: {rag_path}")

            return chromadb.PersistentClient(
                path=str(rag_path),
                settings=Settings(anonymized_telemetry=False),
            )
        else:
            logger.info(f"Using vector database service: {self.rag_config.path}")
            return chromadb.HttpClient(
                host=self.rag_config.host, port=self.rag_config.port
            )

    def _create_embedder(self) -> LocalEmbedder | OpenAIEmbedder:
        match self.rag_config.embedding_provider:
            case "ollama":
                return LocalEmbedder(self.rag_config)
            case "openai":
                return OpenAIEmbedder(self.rag_config)
            case _:
                raise ValueError(
                    f"Unknown provider: {self.rag_config.embedding_provider}"
                )

    def _get_collection_metadata(self) -> dict:
        return {
            "hnsw:space": "cosine",
            "dimension": self.embedder.dimension,
            "embedding_provider": self.rag_config.embedding_provider,
            "embedding_model": self.rag_config.embedding_model,
        }

    def create_client(self, collection_name: str) -> ChromaDBClient:
        try:
            logger.info(
                f"Creating ChromaDB client for collection: {collection_name}..."
            )
            collection = self.get_collection(collection_name)
            logger.info(f"ChromaDB client for collection: {collection_name} created")
        except ValueError as e:
            logger.error(
                f"Error creating ChromaDB client for collection: {collection_name}: {e}"
            )
            raise ValueError(
                f"Error creating ChromaDB client for collection: {collection_name} not found: {e}"
            ) from e

        return ChromaDBClient(
            rag_config=self.rag_config, embedder=self.embedder, collection=collection
        )

    def get_collection(self, name: str) -> Collection:
        try:
            logger.info(f"Getting vector database collection {name}")
            return self.client.get_collection(name=name)
        except ValueError as e:
            logger.error(f"Error getting vector database collection {name}: {e}")
            raise ValueError(f"Vector database collection {name} not found: {e}") from e

    def create_collection(self, name: str) -> bool:
        if self.collection_exists(name):
            logger.info(f"Vector database collection {name} already exists")
            return False

        try:
            self.client.create_collection(
                name=name, metadata=self._get_collection_metadata()
            )
            return True
        except ValueError as e:
            logger.error(f"Error creating vector database collection {name}: {e}")
            raise ValueError(
                f"Error creating vector database collection {name}: {e}"
            ) from e

    def list_collections(self) -> list[str]:
        logger.info("Getting vector database collections list")
        return [c.name for c in self.client.list_collections()]

    def collection_exists(self, name: str) -> bool:
        logger.info(f"Checking vector database collection {name} exists")
        is_exists = name in self.list_collections()
        logger.info(
            f"Vector database collection {name} {'exists' if is_exists else 'does not exist'}"
        )
        return is_exists

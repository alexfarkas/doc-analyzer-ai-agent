import logging
from sentence_transformers import SentenceTransformer

from rag_client import RAGConfigProtocol

logger = logging.getLogger(__name__)


class LocalEmbedder:
    def __init__(self, rag_config: RAGConfigProtocol):
        self.rag_config = rag_config
        self.model = SentenceTransformer(rag_config.embedding_model)
        self.dimension = self.model.get_embedding_dimension()

        logger.info(
            f"Local embedder initialized: model={self.model}, dimension={self.dimension}"
        )

    def encode(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        return self.model.encode(
            texts=texts, show_progress_bar=False, batch_size=10
        ).tolist()

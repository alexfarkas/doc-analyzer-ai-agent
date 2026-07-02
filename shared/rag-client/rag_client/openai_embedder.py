import logging

from openai import OpenAI

from rag_client import RAGConfigProtocol

logger = logging.getLogger(__name__)


class OpenAIEmbedder:
    def __init__(self, rag_config: RAGConfigProtocol):
        self.rag_config = rag_config
        self.client = OpenAI(base_url=rag_config.base_url, api_key=rag_config.api_key)
        self.model = rag_config.embedding_model
        self.dimension = self._probe_dimension()

        logger.info(
            f"OpenAI embedder initialized: model={self.model}, dimension={self.dimension}"
        )

    def _probe_dimension(self):
        try:
            response = self.client.embeddings.create(
                model=self.model, input="dimension_probe", encoding_format="float"
            )
            return len(response.data[0].embedding)
        except Exception as e:
            raise RuntimeError(
                f"Unable to determine dimension of RAG embedding model {self.model} "
                f"Error: {e}"
            ) from e

    def encode(self, texts: list[str]) -> list[list[float]]:
        embeddings = []
        batch_size = 100

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = self.client.embeddings.create(
                model=self.model, input=batch, encoding_format="float"
            )
            embeddings.extend([e.embedding for e in response.data])

        return embeddings

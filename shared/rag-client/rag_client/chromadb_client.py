import logging
from typing import Any

from chromadb.api.models.Collection import Collection

from decorators.timing import time_logging_async
from rag_client import RAGConfigProtocol, LocalEmbedder, OpenAIEmbedder

logger = logging.getLogger(__name__)


class ChromaDBClient:
    def __init__(
        self,
        rag_config: RAGConfigProtocol,
        embedder: LocalEmbedder | OpenAIEmbedder,
        collection: Collection,
    ):
        self.rag_config = rag_config
        self.embedder = embedder
        self.collection = collection

    @property
    def collection_name(self) -> str:
        return self.collection.name

    async def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict] | None = None,
        ids: list[str] | None = None,
    ) -> list[str]:
        logger.info(
            f"Adding {len(documents)} documents to vector database collection..."
        )
        if not documents:
            return []

        embeddings = self.embedder.encode(documents)

        if ids is None:
            logger.info("Ids are not provided, setting default ids")
            ids = [f"doc_{self.collection.count() + i}" for i in range(len(documents))]
        if metadatas is None:
            logger.info("Metadata is not provided, setting empty metadata")
            metadatas = [{} for _ in documents]

        self.collection.add(
            embeddings=embeddings, documents=documents, metadatas=metadatas, ids=ids
        )

        logger.info(f"{len(documents)} documents added to vector database collection")

        return ids

    @time_logging_async
    async def search(
        self,
        query: str,
        top_k: int | None = None,
        threshold: float | None = None,
        formatted: bool = False,
    ) ->list[dict[str, Any]] | str:
        logger.info("Searching vector database")

        top_k = top_k or self.rag_config.top_k
        threshold = threshold or self.rag_config.similarity_threshold

        query_embedding = self.embedder.encode([query])[0]

        if self.collection.count() == 0:
            logger.info("Vector database collection is empty, returning empty list")
            return self._formatted_context([]) if formatted else []

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"],
        )

        relevant = []
        for i, doc in enumerate(results["documents"][0]):
            similarity = 1 - results["distances"][0][i]
            if similarity >= threshold:
                relevant.append(
                    {
                        "content": doc,
                        "metadata": results["metadatas"][0][i],
                        "similarity": round(similarity, 3),
                    }
                )

        if formatted:
            return self._formatted_context(relevant)

        logger.info(f"Found {len(relevant)} relevant documents")
        return relevant

    def _formatted_context(self, results: list[dict[str, Any]]) -> str:
        if not results:
            return ""

        logger.info(
            f"Formatting found {len(results)} relevant documents for passing to LLM..."
        )

        max_length = self.rag_config.max_context_length
        block_length = self.rag_config.context_block_length

        context_blocks = []
        total_length = 0

        for i, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})
            source = (
                metadata.get("source")
                or metadata.get("file_path")
                or metadata.get("url")
                or metadata.get("id")
                or f"fragment_{i}"
            )

            header = f"[{i}] {source}"

            content = result["content"].strip()
            content = "\n".join(
                line.rstrip() for line in content.split("\n") if line.strip()
            )

            if len(content) > block_length:
                content = content[: block_length - 3] + "..."

            block = f"{header}\n{content}"

            if total_length + len(block) + 50 > max_length:
                if i == 1:
                    block = block[: max_length - 100] + "\n[...обрезано...]"
                else:
                    break

            context_blocks.append(block)
            total_length += len(block) + 2

        if not context_blocks:
            return ""

        logger.info("Relevant documents are formatted for passing to LLM")

        return (
            "\n\n--- RAG CONTEXT BEGIN ---\n"
            + "\n\n".join(context_blocks)
            + "\n--- RAG CONTEXT END ---\n\n"
            "Используй приведённую выше информацию из базы знаний для формирования точного ответа. "
            "Если информация противоречит твоим знаниям — приоритет отдавай данным из контекста. "
            "Не упоминай явно, что ты используешь внешние источники."
        )

from rag_client import ChromaDBClient


class RagSearch:
    def __init__(self, chromadb_client: ChromaDBClient):
        self.chromadb_client = chromadb_client

    async def retrieve_document(self, query: str, top_k: int = 3) -> str:
        results = await self.chromadb_client.search(query, top_k)

        if not results:
            return "Relevant data was not found in RAG database"

        chunks = []
        for i, r in enumerate(results, 1):
            chunk_text = r["content"].strip()
            similarity = r.get("similarity", 0)
            source = r.get("metadata", {}).get("source", "не указан")
            file_format = r.get("metadata", {}).get("format", "")

            chunks.append(
                f"[Фрагмент {i}] | Релевантность: {similarity:.2f} | Источник: {source} ({file_format})\n"
                f"{chunk_text}"
            )

        return "\n\n---\n\n".join(chunks)

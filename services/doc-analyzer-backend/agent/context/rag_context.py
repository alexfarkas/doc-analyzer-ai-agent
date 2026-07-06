import logging

from langchain_core.messages import HumanMessage
from rag_client import ChromaDBClientFactory

from agent.context.conversation_storage import ConversationHistory

logger = logging.getLogger(__name__)


async def get_prompts_with_rag(
    prompts: tuple[str, str],
    chromadb_client_factory: ChromaDBClientFactory | None = None,
    rag_collections_names: list[str] | None = None,
) -> tuple[str, str]:
    if not chromadb_client_factory:
        logger.warning("No RAG client factory provided")
        return prompts

    if not rag_collections_names:
        logger.warning("No RAG collections provided")
        return prompts

    chromadb_clients = [
        chromadb_client_factory.create_client(name) for name in rag_collections_names
    ]

    system_prompt, user_prompt = prompts

    rag_query = await _build_rag_query(system_prompt, user_prompt)

    logger.info("Retrieving RAG context...")
    rag_context_parts = []
    for client in chromadb_clients:
        rag_context_parts.append(await client.search(rag_query, formatted=True))
    rag_context = "".join(rag_context_parts)
    logger.info("RAG context is retrieved")

    if rag_context:
        logger.info("RAG context found")
        if user_prompt:
            logger.info("Injecting RAG context to user prompt")
            user_prompt = await _inject_context_into_prompt(user_prompt, rag_context)
        elif system_prompt:
            logger.info("Injecting RAG context to system prompt")
            system_prompt = await _inject_context_into_prompt(
                system_prompt, rag_context
            )
    else:
        logger.info("No RAG context found")

    return user_prompt, system_prompt


async def get_user_prompt_with_rag(
    user_prompt: str,
    history: ConversationHistory,
    chromadb_client_factory: ChromaDBClientFactory | None = None,
    rag_collections_names: list[str] | None = None,
) -> str:
    if not chromadb_client_factory:
        logger.warning("No RAG client factory provided")
        return user_prompt

    if not rag_collections_names:
        logger.warning("No RAG collections provided")
        return user_prompt

    chromadb_clients = [
        chromadb_client_factory.create_client(name) for name in rag_collections_names
    ]
    rag_query = await _build_conversation_rag_query(user_prompt, history)

    logger.info("Retrieving RAG context...")
    rag_context_parts = []
    for client in chromadb_clients:
        rag_context_parts.append(await client.search(rag_query, formatted=True))
    rag_context = "".join(rag_context_parts)
    logger.info("RAG context is retrieved")

    if rag_context:
        return await _inject_context_into_prompt(user_prompt, rag_context)

    return user_prompt


async def _build_rag_query(system_prompt: str | None, user_prompt: str | None) -> str:
    parts = []
    system_prompt_snippet_length = 200
    user_prompt_snippet_length = 300
    query_length = 500

    if system_prompt:
        system_snippet = (
            system_prompt[:system_prompt_snippet_length]
            if len(system_prompt) > system_prompt_snippet_length
            else system_prompt
        )
        parts.append(f"Роль/задача: {system_snippet}")

    if user_prompt:
        user_snippet = (
            user_prompt[:user_prompt_snippet_length]
            if len(user_prompt) > user_prompt_snippet_length
            else user_prompt
        )
        parts.append(f"Запрос: {user_snippet}")

    query = "\n".join(parts)
    return query[:query_length]


async def _build_conversation_rag_query(
    new_message: str, history: ConversationHistory
) -> str:
    last_messages_count = 2
    last_messages_lookup_count = 6

    max_new_message_length = 200
    max_recent_message_length = 150
    query_length = 400

    recent_context = []
    for msg in reversed(history.get_last_messages(last_messages_lookup_count)):
        if isinstance(msg, HumanMessage) and len(recent_context) < last_messages_count:
            recent_context.append(msg.content[:max_recent_message_length])

    parts = recent_context + [new_message[:max_new_message_length]]
    query = "\n".join(parts)
    return query.strip()[:query_length]


async def _inject_context_into_prompt(prompt: str, context: str) -> str:
    if not context:
        return prompt

    context_block = (
        "### Контекст из базы знаний (RAG)\n"
        "Ниже приведена релевантная информация из внутренней базы знаний. "
        "Используй её для повышения точности ответа, но не упоминай явно, что ты используешь внешние источники.\n\n"
        f"{context}\n\n"
        "### Конец контекста\n"
    )

    return f"{prompt}{context_block}"

import logging
import time
from typing import AsyncGenerator

from db_repository import PromptRepository
from langchain_core.language_models import BaseChatModel
from rag_client import ChromaDBClientFactory

from src.doc_analyzer_backend.agent.context.conversation_storage import ConversationHistory
from src.doc_analyzer_backend.agent.messages_data.chat_utils import prepare_chat_messages, stream_llm_response, \
    finalize_chat_stream

logger = logging.getLogger(__name__)


async def agent_chat_stream(
    agent_id: int,
    user_message: str,
    llm: BaseChatModel,
    provider: str,
    model: str | None,
    history: ConversationHistory,
    prompt_repository: PromptRepository | None,
    chromadb_client_factory: ChromaDBClientFactory | None,
    rag_collections_names: list[str],
) -> AsyncGenerator[str, None]:
    start = time.perf_counter()
    logger.info(f"Agent {agent_id}: chat stream is starting...")

    logger.debug(f"History system prompt{history.system_prompt}")

    messages = await prepare_chat_messages(
        user_message=user_message,
        history=history,
        prompt_repository=prompt_repository,
        chromadb_client_factory=chromadb_client_factory,
        rag_collections_names=rag_collections_names,
    )

    history.trim()

    accumulated_content = []
    try:
        async for chunk in stream_llm_response(
            llm=llm,
            messages=messages,
            accumulated_content=accumulated_content,
        ):
            yield chunk
    except Exception as e:
        logger.error(f"Streaming error: {e}")
        yield f"\n\n[Ошибка генерации ответа: {str(e)}]"
        return
    finally:
        full_answer = "".join(accumulated_content)
        if full_answer:
            finalize_chat_stream(
                user_message=user_message,
                full_answer=full_answer,
                messages=messages,
                provider=provider,
                model=model,
                history=history,
                start_time=start,
            )

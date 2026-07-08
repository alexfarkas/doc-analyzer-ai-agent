import logging
import time
from typing import AsyncGenerator

from agent_enums import Mode
from db_repository import PromptRepository
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessageChunk
from rag_client import ChromaDBClientFactory

from src.doc_analyzer_backend.agent.context.conversation_storage import ConversationHistory
from src.doc_analyzer_backend.agent.context.prompts_storage import get_prompts
from src.doc_analyzer_backend.agent.context.rag_context import get_user_prompt_with_rag
from src.doc_analyzer_backend.agent.messages_data.messages_utils import build_messages
from src.doc_analyzer_backend.agent.models.chat_metadata import ChatMetadata
from src.doc_analyzer_backend.llm.tokens.token_counter import calculate_stream_tokens_usage
from src.doc_analyzer_backend.llm.tokens.token_usage import create_token_usage, TokenUsage
from src.doc_analyzer_backend.llm.tokens.total_token_usage_utils import update_and_get_total_token_usage

logger = logging.getLogger(__name__)


async def prepare_chat_messages(
    user_message: str,
    history: ConversationHistory,
    prompt_repository: PromptRepository | None,
    chromadb_client_factory: ChromaDBClientFactory | None,
    rag_collections_names: list[str],
) -> list[BaseMessage]:
    init_user_prompt = user_message
    logger.debug(f"User prompt in chat:\n{init_user_prompt}")

    if chromadb_client_factory and rag_collections_names:
        init_user_prompt = await get_user_prompt_with_rag(
            init_user_prompt,
            history,
            chromadb_client_factory,
            rag_collections_names,
        )
    logger.debug(f"User prompt with RAG in chat:\n{init_user_prompt}")

    prompts = await get_prompts(
        mode=Mode.CHAT,
        prompt_repository=prompt_repository,
        init_system_prompt=history.system_prompt,
        init_user_prompt=init_user_prompt,
        history=history.as_string(),
    )

    return build_messages(prompts, Mode.CHAT)


async def stream_llm_response(
    llm: BaseChatModel,
    messages: list[BaseMessage],
    accumulated_content: list[str],
) -> AsyncGenerator[str, None]:
    async for chunk in llm.astream(messages):
        content = _extract_chunk_content(chunk)
        if content:
            accumulated_content.append(content)
            yield content


def _extract_chunk_content(chunk: AIMessageChunk) -> str | None:
    if hasattr(chunk, "content") and chunk.content:
        return chunk.content
    elif isinstance(chunk, dict) and "content" in chunk:
        return chunk["content"]
    elif hasattr(chunk, "delta") and hasattr(chunk.delta, "content"):
        return chunk.delta.content
    return None


async def finalize_chat_stream(
    user_message: str,
    full_answer: str,
    messages: list[BaseMessage],
    model: str,
    history: ConversationHistory,
    token_usage: TokenUsage,
    start_time: float,
):
    history.save_user_prompt(user_message)
    history.save_ai_message(full_answer)

    system_prompt = messages[0].content
    user_prompt = messages[1].content

    input_tokens = await calculate_stream_tokens_usage(
        f"{system_prompt}\n{user_prompt}", model
    )
    output_tokens = await calculate_stream_tokens_usage(full_answer, model)

    chat_stream_token_usage = create_token_usage(
        input_tokens=input_tokens, output_tokens=output_tokens
    )
    token_usage.add_usage(chat_stream_token_usage)
    logger.info(f"Chat stream token usage: {chat_stream_token_usage}")
    logger.info(f"Overall token usage: {token_usage}")

    elapsed = time.perf_counter() - start_time
    logger.info(f"Chat stream is completed in {elapsed} seconds")

    total_token_usage = await update_and_get_total_token_usage(token_usage)

    result = ChatMetadata(
        token_usage=token_usage.model_dump(),
        total_token_usage=total_token_usage.model_dump(),
        elapsed=elapsed,
        cost_rub=0,
    ).model_dump()
    yield f"\n__METADATA__:{result}"

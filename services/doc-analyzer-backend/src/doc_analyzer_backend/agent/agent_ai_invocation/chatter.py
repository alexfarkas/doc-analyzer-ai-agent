import logging

from agent_enums import Mode
from db_repository import PromptRepository
from langgraph.graph.state import CompiledStateGraph
from rag_client import ChromaDBClientFactory

from src.doc_analyzer_backend.agent.agent_ai_invocation.ai_invocation import ai_invoke_track
from src.doc_analyzer_backend.agent.context.conversation_storage import ConversationHistory
from src.doc_analyzer_backend.agent.context.prompts_storage import get_prompts
from src.doc_analyzer_backend.agent.context.rag_context import get_user_prompt_with_rag
from src.doc_analyzer_backend.agent.messages_data.agent_data_builder import build_doc_analyse_data
from src.doc_analyzer_backend.agent.messages_data.messages_utils import build_messages

logger = logging.getLogger(__name__)


async def agent_chat(
    agent_id: int,
    app: CompiledStateGraph,
    user_message: str,
    provider: str,
    model: str | None,
    history: ConversationHistory,
    prompt_repository: PromptRepository | None,
    chromadb_client_factory: ChromaDBClientFactory | None,
    rag_collections_names: list[str],
):
    logger.debug(f"History system prompt{history.system_prompt}")

    init_user_prompt = user_message
    logger.debug(f"User prompt in chat:\n{init_user_prompt}")

    if chromadb_client_factory and rag_collections_names:
        init_user_prompt = await get_user_prompt_with_rag(
            init_user_prompt,
            history,
            chromadb_client_factory,
            rag_collections_names,
        )

    prompts = await get_prompts(
        mode=Mode.CHAT,
        prompt_repository=prompt_repository,
        init_system_prompt=history.system_prompt,
        init_user_prompt=init_user_prompt,
        history=history.as_string(),
    )

    messages = build_messages(prompts, Mode.CHAT)

    history.trim()

    final_msg, consumption_data = await ai_invoke_track(
        agent_id=agent_id,
        app=app,
        messages=messages,
        provider=provider,
        model=model,
        type_message="chat",
    )

    history.save_user_prompt(user_message)
    history.save_ai_message(final_msg)

    return build_doc_analyse_data(
        final_msg=final_msg,
        consumption_data=consumption_data,
    )

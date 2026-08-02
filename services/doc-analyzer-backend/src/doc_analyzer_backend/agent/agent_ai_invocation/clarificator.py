import logging

from agent_enums import Mode, AnswerStatus
from db_repository import PromptRepository
from langgraph.graph.state import CompiledStateGraph
from rag_client import ChromaDBClientFactory

from src.doc_analyzer_backend.agent.agent_ai_invocation.ai_invocation import ai_invoke_track
from src.doc_analyzer_backend.agent.context.conversation_storage import ConversationHistory
from src.doc_analyzer_backend.agent.context.prompts_storage import get_prompts
from src.doc_analyzer_backend.agent.context.rag_context import get_prompts_with_rag
from src.doc_analyzer_backend.agent.messages_data.agent_data_builder import build_doc_analyse_data
from src.doc_analyzer_backend.agent.messages_data.messages_utils import build_messages
from src.doc_analyzer_backend.session.data.user_data import UserData

logger = logging.getLogger(__name__)


async def agent_clarify(
    data: UserData,
    agent_id: int,
    app: CompiledStateGraph,
    ai_answer: str,
    user_message: str,
    answer_index: int,
    provider: str,
    model: str | None,
    history: ConversationHistory,
    prompt_repository: PromptRepository | None,
    chromadb_client_factory: ChromaDBClientFactory | None,
    rag_collections_names: list[str],
):
    init_user_prompt = user_message
    logger.debug(f"User clarification message: {init_user_prompt}")

    if chromadb_client_factory and rag_collections_names:
        _, init_user_prompt = await get_prompts_with_rag(
            ("", init_user_prompt),
            chromadb_client_factory,
            rag_collections_names,
        )

    answer_seq = data.get_answer_seq(answer_index)
    clarifying_answer = next((a for a in answer_seq.answers if a.status == AnswerStatus.FINAL), None)
    logger.debug(f"Final AI answer to clarify: {clarifying_answer}")

    prompts = await get_prompts(
        mode=Mode.CLARIFICATION,
        prompt_repository=prompt_repository,
        init_system_prompt=history.system_prompt,
        init_user_prompt=init_user_prompt,
        ai_answer=ai_answer,
        clarifying_answer=clarifying_answer,
    )

    messages = build_messages(prompts, Mode.CLARIFICATION)

    final_msg, consumption_data = await ai_invoke_track(
        agent_id=agent_id,
        app=app,
        messages=messages,
        provider=provider,
        model=model,
        type_message="clarification",
    )

    return build_doc_analyse_data(
        final_msg=final_msg,
        consumption_data=consumption_data,
    )

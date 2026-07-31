import logging

from agent_enums import Role, Assignment, Mode
from db_repository import PromptRepository
from langgraph.graph.state import CompiledStateGraph
from rag_client import ChromaDBClientFactory

from src.doc_analyzer_backend.agent.agent_ai_invocation.ai_invocation import ai_invoke_track
from src.doc_analyzer_backend.agent.consumption_counters.token_counter import calculate_tokens_usage
from src.doc_analyzer_backend.agent.context.conversation_storage import ConversationHistory
from src.doc_analyzer_backend.agent.context.prompts_storage import get_prompts
from src.doc_analyzer_backend.agent.context.rag_context import get_prompts_with_rag
from src.doc_analyzer_backend.agent.messages_data.agent_data_builder import build_doc_analyse_data
from src.doc_analyzer_backend.agent.messages_data.messages_utils import build_messages
from src.doc_analyzer_backend.agent.models.analysis.agent_analysis_data import AgentAnalysisData

logger = logging.getLogger(__name__)


async def agent_analyze_doc(
    agent_id: int,
    app: CompiledStateGraph,
    resources: list[str],
    role: Role,
    assignment: Assignment,
    provider: str,
    model: str,
    limit: int | None,
    history: ConversationHistory,
    prompt_repository: PromptRepository | None,
    chromadb_client_factory: ChromaDBClientFactory | None,
    rag_collections_names: list[str],
) -> AgentAnalysisData:
    if limit:
        logger.info(f"Tokens limit: {limit}")
    else:
        logger.info("Tokens limit is not set")

    prompts = await get_prompts(
        mode=Mode.ANALYSIS,
        role=role,
        assignment=assignment,
        prompt_repository=prompt_repository,
        resources=resources,
    )

    history.clear()

    if chromadb_client_factory and rag_collections_names:
        prompts = await get_prompts_with_rag(
            prompts, chromadb_client_factory, rag_collections_names
        )

    history.save(prompts)

    messages = build_messages(prompts, Mode.ANALYSIS)

    estimated_tokens = calculate_tokens_usage(messages, model)
    logger.info(f"Estimated input tokens: {estimated_tokens}")

    final_msg, consumption_data = await ai_invoke_track(
        agent_id=agent_id,
        app=app,
        messages=messages,
        provider=provider,
        model=model,
        type_message="doc analysis",
    )

    history.save_ai_message(final_msg)

    return build_doc_analyse_data(
        final_msg=final_msg,
        consumption_data=consumption_data,
    )

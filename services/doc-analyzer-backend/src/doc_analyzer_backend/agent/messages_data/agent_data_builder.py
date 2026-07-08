from agent_enums import Assignment, AnswerStatus

from src.doc_analyzer_backend.agent.models.agent_analysis_data import AgentAnalysisData
from src.doc_analyzer_backend.api.models.analisys.answer_item import AnswerItem
from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage


def build_doc_analyse_data(
    final_msg: str,
    token_usage: TokenUsage,
    elapsed: float,
    cost_rub: float,
) -> AgentAnalysisData:
    return AgentAnalysisData(
        answer_item=AnswerItem(
            answer=final_msg,
            author=Assignment.EXEC,
            status=AnswerStatus.FINAL,
            init_status=AnswerStatus.FINAL,
        ),
        token_usage=token_usage,
        elapsed=elapsed,
        cost_rub=cost_rub,
    )

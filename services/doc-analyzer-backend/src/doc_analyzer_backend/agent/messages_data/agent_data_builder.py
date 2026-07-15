from agent_enums import Assignment, AnswerStatus

from src.doc_analyzer_backend.agent.models.analysis.agent_analysis_data import (
    AgentAnalysisData,
)
from src.doc_analyzer_backend.agent.models.tokens.consumption_data import (
    ConsumptionData,
)
from src.doc_analyzer_backend.api.models.analisys.answer_item import AnswerItem


def build_doc_analyse_data(
    final_msg: str,
    consumption_data: ConsumptionData,
) -> AgentAnalysisData:
    return AgentAnalysisData(
        answer_item=AnswerItem(
            answer=final_msg,
            author=Assignment.EXEC,
            status=AnswerStatus.FINAL,
            init_status=AnswerStatus.FINAL,
        ),
        consumption_data=consumption_data,
    )

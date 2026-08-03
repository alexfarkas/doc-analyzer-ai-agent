from src.doc_analyzer_backend.agent.models.analysis.agent_analysis_data import (
    AgentAnalysisData,
)
from src.doc_analyzer_backend.agent.models.analysis.council_analysis_data import (
    CouncilAnalysisData,
)
from tests.consts.agent import DEFAULT_ANSWER, DEFAULT_JUDGEMENTS, DEFAULT_SCORES, DEFAULT_ANSWER_COUNT
from tests.factories.answers import make_answer_item, make_answer_seq
from tests.factories.tokens import make_consumption_data


def make_agent_analyze_doc() -> AgentAnalysisData:
    """
    Data for single agent mock

    Returns:
        Agent analysis result data
    """
    return AgentAnalysisData(
        answer_item=make_answer_item(DEFAULT_ANSWER),
        consumption_data=make_consumption_data(),
    )


def make_council_analyze_doc() -> CouncilAnalysisData:
    """
    Data for council mock

    Returns:
        Council analysis result data
    """
    return CouncilAnalysisData(
        answer_seqs=[
            make_answer_seq(answers_count=DEFAULT_ANSWER_COUNT),
            make_answer_seq(answers_count=DEFAULT_ANSWER_COUNT),
        ],
        judgements=DEFAULT_JUDGEMENTS,
        scores=DEFAULT_SCORES,
        consumption_data=make_consumption_data(),
    )

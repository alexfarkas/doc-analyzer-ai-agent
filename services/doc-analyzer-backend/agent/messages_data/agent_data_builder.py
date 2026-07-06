from agent.models.agent_analysis_data import AgentAnalysisData
from api.models.analisys.answer_item import AnswerItem
from llm.tokens.token_usage import TokenUsage


def build_doc_analyse_data(
    final_msg: str,
    token_usage: TokenUsage,
    elapsed: float,
    cost_rub: float,
) -> AgentAnalysisData:
    return AgentAnalysisData(
        answer_item=AnswerItem(
            answer=final_msg,
            author="exec",
            status="final",
            init_status="final",
        ),
        token_usage=token_usage,
        elapsed=elapsed,
        cost_rub=cost_rub,
    )

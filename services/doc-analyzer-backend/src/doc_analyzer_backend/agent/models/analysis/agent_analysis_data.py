from pydantic import BaseModel

from src.doc_analyzer_backend.agent.models.tokens.consumption_data import ConsumptionData
from src.doc_analyzer_backend.api.models.analisys.answer_item import AnswerItem


class AgentAnalysisData(BaseModel):
    answer_item: AnswerItem
    consumption_data: ConsumptionData

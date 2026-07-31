import logging

from src.doc_analyzer_backend.api.models.analisys.answer_item import AnswerItem
from src.doc_analyzer_backend.api.models.analisys.answer_seq import AnswerSeq
from src.doc_analyzer_backend.data.app_state_manager import app_state

logger = logging.getLogger(__name__)


async def update_answer_item(answer_item: AnswerItem):
    logger.info("Updating answer item in app data")
    await app_state.set_answer_seqs(answer_item)


async def update_answer_seqs(answer_seqs: list[AnswerSeq]):
    logger.info("Updating answer seqs in app data")
    await app_state.set_answer_seqs(answer_seqs)

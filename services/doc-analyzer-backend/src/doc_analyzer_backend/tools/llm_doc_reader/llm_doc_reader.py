import logging
from pathlib import Path

import pytesseract

from src.doc_analyzer_backend.tools.llm_doc_reader.llm_doc_reader_config import (
    LLMDocReaderConfig,
)
from src.doc_analyzer_backend.tools.llm_doc_reader.consts import RE_URL
from src.doc_analyzer_backend.tools.llm_doc_reader.file_parsers import FileParser
from src.doc_analyzer_backend.tools.llm_doc_reader.text_optimizer import TextOptimizer
from src.doc_analyzer_backend.tools.llm_doc_reader.web_parsers import WebParser

logger = logging.getLogger(__name__)


class LLMDocReader:
    """
    Универсальный оффлайн-извлекатель контента.
    Принимает: путь к файлу, URL или сырой текст.
    Возвращает: структурированный Markdown, оптимизированный для LLM-анализа.
    """

    def __init__(self, config: LLMDocReaderConfig = LLMDocReaderConfig()):
        self.config = config

        self.file_parsers = FileParser(config)
        self.web_parsers = WebParser(config)
        self.text_optimizer = TextOptimizer()

        if config.ocr_enabled:
            self._check_ocr()

    def _check_ocr(self):
        try:
            pytesseract.get_tesseract_version()
            self.config.ocr_enabled = True
        except Exception:
            logger.warning(
                "Tesseract is not found. OCR for images and scans is disabled."
            )
            self.config.ocr_enabled = False

    def read_file(self, file_path: str) -> str:
        return self.file_parsers.read_file(Path(file_path))

    def read_url(self, url: str) -> str:
        return self.web_parsers.fetch_url(url)

    def read_data(self, input_data) -> str:
        return self.text_optimizer.optimize_text(input_data)

    def process(self, input_data: str) -> str:
        """Маршрутизатор входных данных: файл → URL → текст."""
        if RE_URL.match(input_data):
            return self.web_parsers.fetch_url(input_data)
        if Path(input_data).is_file():
            return self.file_parsers.read_file(Path(input_data))
        return self.text_optimizer.optimize_text(input_data)

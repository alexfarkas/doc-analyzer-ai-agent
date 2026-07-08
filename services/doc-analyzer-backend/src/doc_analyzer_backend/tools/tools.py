import logging
import os
import uuid

from langchain_core.tools import tool
from rag_client import ChromaDBClient

from src.doc_analyzer_backend.config.app_config import app_config
from src.doc_analyzer_backend.decorators.timing import tool_time_logging_async
from src.doc_analyzer_backend.tools.llm_doc_reader.llm_doc_reader import LLMDocReader
from src.doc_analyzer_backend.tools.rag_search.rag_search import RagSearch

logger = logging.getLogger(__name__)


def init_tools():
    tools = [read_document_file, read_web_page_from_url]

    return tools


@tool
@tool_time_logging_async
async def read_document_file(file_path: str):
    """
    Читает текстовый файл по указанному пути.
    Используй этот инструмент, когда:
    - Пользователь просит прочитать, проанализировать или извлечь информацию из файла
    - В запросе указан путь к тексотовому файлу (.txt, .rtf, .doc, .docx, .pdf, .md, .py, .json и т.д.)
    - Нужно получить содержимое текстового файла для дальнейшей обработки
    - Нужно получить содержимое текстового документа для дальнейшего анализа
    Параметры:
    - file_path: абсолютный или относительный путь к файлу
    Возвращает: полный текст файла в виде строки.
    """
    return LLMDocReader().read_file(file_path)


@tool
@tool_time_logging_async
async def read_web_page_from_url(url: str):
    """
    Открывает веб-страницу по указанному URL и читает содержимое этой веб-страницы
    Используй этот инструмент, когда:
    - Пользователь просит прочитать, проанализировать или извлечь информацию с веб-страницы
    Параметры:
    - url: адрес ресурса или веб-страницы
    Возвращает: содержимое веб-страницы в виде строки
    """
    result = LLMDocReader().read_url(url)
    await _write_web_page_data_to_file(result, url)
    return result


async def _write_web_page_data_to_file(text: str, url: str):
    upload_dir = os.path.join(os.getcwd(), app_config.docs_dir)
    safe_url = "".join(c if c.isalnum() or c in "_-" else "_" for c in url)
    file_name = f"{safe_url}-{uuid.uuid4().hex[:10]}.md"
    file_path = os.path.join(upload_dir, file_name)

    with open(file_path, "w") as file:
        file.write(text)


def create_rag_search_tool(chromadb_client: ChromaDBClient):
    rag_search = RagSearch(chromadb_client)

    @tool
    @tool_time_logging_async
    async def retrieve_document_from_vector_storage(query: str, top_k: int = 3):
        """
        Ищет релевантные данные в базе знаний
        Используй этот инструмент каждый раз
        Ищи реоевантные запросу пользователя данные а базе знаний и добавляй их в контекст основного запроса
        Параметры:
        - query: поисковый запрос на естесственном языке (не более 50 слов)
        - top_k: количество возвращаемых в ответе фрагментов (от 1 до 10, по умолчанию 3)
        Возвращает: строку с найденными в базе знаний данными
        """
        return await rag_search.retrieve_document(query, top_k)

    return retrieve_document_from_vector_storage

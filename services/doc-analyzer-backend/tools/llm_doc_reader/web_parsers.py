import logging
from pathlib import Path

import httpx
from bs4 import BeautifulSoup

from tools.llm_doc_reader.llm_doc_reader_config import LLMDocReaderConfig
from tools.llm_doc_reader.consts import RE_EMPTY_LINES
from tools.llm_doc_reader.utils import assemble_markdown

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
#  Веб-парсер
# ──────────────────────────────────────────────────────────────
class WebParser:
    def __init__(self, config: LLMDocReaderConfig):
        self.config = config

    def fetch_url(self, url: str) -> str:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        with httpx.Client(
            follow_redirects=True, timeout=15.0, headers=headers
        ) as client:
            resp = client.get(url)

            try:
                resp.raise_for_status()

                soup = BeautifulSoup(resp.text, "lxml")
                for tag in soup(
                    [
                        "script",
                        "style",
                        "nav",
                        "footer",
                        "header",
                        "iframe",
                        "noscript",
                        "form",
                    ]
                ):
                    tag.decompose()
                text = RE_EMPTY_LINES.sub(
                    "\n\n", soup.get_text(separator="\n", strip=True)
                ).strip()
                meta = {
                    "title": soup.title.string.strip() if soup.title else "",
                    "url": url,
                }

                return assemble_markdown(
                    [text], [], Path(url), self.config, extra_meta=meta
                )
            except httpx.HTTPStatusError as e:
                logger.error(f"Error fetching URL {url}: {e}")

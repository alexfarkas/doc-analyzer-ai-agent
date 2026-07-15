import zipfile
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
import pytesseract
from PIL import Image

from src.doc_analyzer_backend.tools.llm_doc_reader.consts import RE_WHITESPACE
from src.doc_analyzer_backend.tools.llm_doc_reader.llm_doc_reader_config import (
    LLMDocReaderConfig,
)


# ──────────────────────────────────────────────────────────────
#  Утилиты: таблицы, OCR, сборка Markdown
# ──────────────────────────────────────────────────────────────
def table_to_md(table, is_pdf: bool = False) -> str | None:
    rows = []
    if is_pdf:
        rows = [[sanitize(c) for c in r] for r in table]
    else:
        for r in table.rows:
            rows.append([sanitize(c) for c in r.cells])
    rows = [r for r in rows if any(c.strip() for c in r)]
    if not rows:
        return None
    max_c = max(len(r) for r in rows)
    rows = [r + [""] * (max_c - len(r)) for r in rows]
    return "\n".join(
        [" | ".join(rows[0]), " | ".join(["---"] * max_c)]
        + [" | ".join(r) for r in rows[1:]]
    )


def sanitize(cell) -> str:
    txt = getattr(cell, "text", None) or str(cell)
    return RE_WHITESPACE.sub(" ", txt.replace("\n", " ").strip())[:150]


def extract_office_images(path: Path, media_dir: str) -> list[dict]:
    imgs = []
    try:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if name.startswith(media_dir):
                    imgs.append({"bytes": z.read(name), "idx": len(imgs) + 1})
    except:
        pass
    return imgs


def run_ocr(img_bytes: bytes, config: LLMDocReaderConfig) -> str:
    if not config.ocr_enabled:
        return "[OCR отключен. Установите tesseract-ocr]"
    try:
        img = Image.open(BytesIO(img_bytes))
        if config.preprocess_images:
            arr = np.array(img.convert("L"))
            arr = cv2.GaussianBlur(arr, (3, 3), 0)
            arr = cv2.adaptiveThreshold(
                arr, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            img = Image.fromarray(arr)
        text = pytesseract.image_to_string(img, lang=config.ocr_lang).strip()
        return text[:2000] if text else "[Текст не распознан]"
    except Exception as e:
        return f"[OCR ошибка: {e}]"


def assemble_markdown(
    blocks: list[str],
    images: list[dict],
    path: Path,
    config: LLMDocReaderConfig,
    extra_meta: dict = {},
) -> str:
    img_md = []
    for img in images:
        ocr = run_ocr(img["bytes"], config)
        img_md.append(f"**Изображение {img['idx']}**\n OCR-содержимое: {ocr}\n")

    full = "\n\n".join(blocks + img_md)
    if len(full) > config.max_output_chars:
        full = (
            full[: config.max_output_chars].rstrip()
            + "\n\n[Содержимое обрезано из-за лимита контекста LLM]"
        )

    meta = {
        "source": str(path),
        "format": path.suffix if path.suffix else "url/text",
        **extra_meta,
    }
    header = f"**Файл/Источник:** {meta.get('title', meta['source'])}\n**Формат:** {meta['format']}\n{'=' * 60}\n\n"
    return header + full

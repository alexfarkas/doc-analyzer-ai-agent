import base64
import zipfile
from pathlib import Path

from src.doc_analyzer_backend.components.preview_reader.preview_reader import IMAGE_MIMES


# ──────────────────────────────────────────────────────────────
#  Утилиты
# ──────────────────────────────────────────────────────────────
def normalize_rows(rows: list[list[str]]) -> list[list[str]]:
    """Выравнивает таблицу по максимальной ширине колонок."""
    if not rows:
        return []
    max_len = max(len(r) for r in rows)
    return [r + [""] * (max_len - len(r)) for r in rows]


def extract_zip_media(path: Path, media_dir: str) -> list[dict]:
    imgs = []
    try:
        with zipfile.ZipFile(path) as z:
            for name in z.namelist():
                if name.startswith(media_dir):
                    ext = Path(name).suffix.lower()
                    mime = IMAGE_MIMES.get(ext, "application/octet-stream")
                    b64 = base64.b64encode(z.read(name)).decode()
                    imgs.append(
                        {"src": f"data:{mime};base64,{b64}", "name": Path(name).name}
                    )
    except:
        pass
    return imgs

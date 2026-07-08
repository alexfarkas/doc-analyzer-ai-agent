from src.doc_analyzer_backend.tools.llm_doc_reader.consts import RE_EMPTY_LINES, RE_WHITESPACE


# ──────────────────────────────────────────────────────────────
#  Оптимизатор текста для передачи LLM
# ──────────────────────────────────────────────────────────────
class TextOptimizer:
    def optimize_text(self, text: str) -> str:
        clean = RE_EMPTY_LINES.sub("\n\n", RE_WHITESPACE.sub(" ", text).strip())
        return f"**Тип:** raw_text\n{'=' * 60}\n\n{clean}"

import re

# Прекомпилированные регулярные выражения
RE_WHITESPACE = re.compile(r"[ \t]+")
RE_NEWLINES = re.compile(r"\r\n|\r")
RE_EMPTY_LINES = re.compile(r"\n{3,}")
RE_URL = re.compile(r"^https?://", re.IGNORECASE)

# Маппинг расширений на языки для подсветки
CODE_LANG_MAP = {
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",
    ".java": "java",
    ".cpp": "cpp",
    ".c": "c",
    ".h": "c",
    ".sh": "bash",
    ".zsh": "bash",
    ".ps1": "powershell",
    ".sql": "sql",
    ".go": "go",
    ".rs": "rust",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".cs": "csharp",
}

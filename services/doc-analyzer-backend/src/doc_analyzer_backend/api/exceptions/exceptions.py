from src.doc_analyzer_backend.config.app_config import app_config


class BaseAgentError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class AgentFileNotFoundError(BaseAgentError):
    def __init__(self, file_path: str):
        super().__init__(f"File not found: {file_path}")


class AgentDirectoryInsteadOfFileError(BaseAgentError):
    def __init__(self, file_path: str):
        super().__init__(f"File expected but directory received: {file_path}")


class AgentFileInsteadOfDirectoryError(BaseAgentError):
    def __init__(self, dir_path: str):
        super().__init__(f"Directory expected but file received: {dir_path}")


class AgentsListIsEmptyError(BaseAgentError):
    def __init__(self):
        super().__init__("Agents list is empty")


class AgentFileTooLargeForPreviewError(BaseAgentError):
    def __init__(self, file_path: str, file_size: int):
        super().__init__(
            f"File {file_path} too large for preview: {file_size / 1024 / 1024:.2f} MB"
        )


class AgentUnsupportedFileExtensionError(BaseAgentError):
    def __init__(self, file_path: str):
        super().__init__(
            f"File {file_path} extension not supported. Supported extensions: {', '.join(app_config.allowed_exts)}"
        )


class AgentFilePreviewError(BaseAgentError):
    def __init__(self, file_path: str):
        super().__init__(f"File {file_path} preview error")

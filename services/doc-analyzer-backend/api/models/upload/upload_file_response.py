from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    file_path: str
    filename: str

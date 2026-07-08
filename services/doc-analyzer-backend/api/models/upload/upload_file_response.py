from pydantic import BaseModel, Field


class UploadFileResponse(BaseModel):
    file_path: str = Field(..., description="Upload file path")
    filename: str = Field(..., description="Upload file name")

import logging
import os
import uuid

from fastapi import UploadFile, File

from api.exceptions.exceptions import AgentUnsupportedFileExtensionError
from config.app_config import app_config

logger = logging.getLogger(__name__)


async def upload_file(file: UploadFile = File(...)):
    file_name = file.filename
    _, ext = os.path.splitext(file_name.lower())

    if ext not in app_config.allowed_exts:
        raise AgentUnsupportedFileExtensionError(file_name)

    upload_dir = os.path.join(os.getcwd(), app_config.docs_dir)

    base = os.path.splitext(file_name)[0]
    safe_base = "".join(c if c.isalnum() or c in "._-" else "_" for c in base)
    final_name = f"{safe_base}_{uuid.uuid4().hex[:10]}{ext}"
    file_path = os.path.join(upload_dir, final_name)

    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    return {"file_path": os.path.abspath(file_path), "filename": final_name}

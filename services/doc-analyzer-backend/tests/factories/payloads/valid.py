from io import BytesIO

from agent_enums import Role, Assignment

from tests.consts.agent import DEFAULT_ROLE, DEFAULT_RESOURCES, DEFAULT_ASSIGNMENT
from tests.consts.filelist import (
    EXPECTED_FILELIST_SORT_FIELDS,
    EXPECTED_FILELIST_SORT_ORDERS,
    DEFAULT_FILELIST_FILE_EXT,
    DEFAULT_FILELIST_FILE_BASE_NAME,
    DEFAULT_FILELIST_FILTER_EXT,
    DEFAULT_PAGINATION_PAGE,
    DEFAULT_PAGINATION_LIMIT,
    DEFAULT_FILELIST_FILE_SIZE,
)
from tests.consts.files import (
    DEFAULT_FILENAME_WITH_EXT,
    DEFAULT_FILE_CONTENT,
    DEFAULT_FILE_CONTENT_TYPE,
)
from tests.consts.llm import DEFAULT_LLM_MODEL
from tests.consts.preview import (
    DEFAULT_PREVIEW_FILE_PATH,
    VALID_PREVIEW_FILE_SIZE,
    DEFAULT_PREVIEW_FILENAME_WITH_EXT,
)
from tests.consts.urls import DEFAULT_URL


def make_doc_analyze_payload(
    resources: list[str] | None = None,
    role: Role | None = DEFAULT_ROLE,
    agents: list[dict] | None = None,
):
    """
    Payload for POST /doc/analyze

    Args:
        resources: list of resources to analyze
        role: agent role
        agents: list of agents configurations

    Returns:
        Payload for POST /doc/analyze
    """
    if resources is None:
        resources = DEFAULT_RESOURCES
    return {
        "resources": resources,
        "role": role,
        "agents": agents or [make_agent_config_block()],
    }


def make_council_doc_analyze_payload(
    resources: list[str] | None = None,
    role: Role | None = DEFAULT_ROLE,
):
    """
    Payload for POST /doc/analyze for council

    Args:
        resources: list of resources to analyze
        role: council agents role

    Returns:
        Payload for POST /doc/analyze with several agents configurations
    """
    if resources is None:
        resources = DEFAULT_RESOURCES
    return make_doc_analyze_payload(
        resources=resources,
        role=role,
        agents=[
            make_agent_config_block(Assignment.EXEC),
            make_agent_config_block(Assignment.CORRECTOR),
        ],
    )


def make_agent_config_block(
    model: str = DEFAULT_LLM_MODEL,
    assignment: Assignment = DEFAULT_ASSIGNMENT,
):
    """
    Single agent configuration block in payload for POST /doc/analyze

    Args:
        model: llm model name
        assignment: agent assignment

    Returns:
        Agent configuration block
    """
    return {
        "model": model,
        "assignment": assignment,
    }


def make_file_payload(
    filename: str = DEFAULT_FILENAME_WITH_EXT,
    content: bytes = DEFAULT_FILE_CONTENT,
    content_type: str = DEFAULT_FILE_CONTENT_TYPE,
) -> dict:
    return {
        "file": (filename, BytesIO(content), content_type),
    }


def make_url_payload(url: str = DEFAULT_URL) -> dict:
    return {"url": url}


def make_preview_params(
    file_path: str = f"{DEFAULT_PREVIEW_FILE_PATH}/{DEFAULT_PREVIEW_FILENAME_WITH_EXT}",
    max_size: int = VALID_PREVIEW_FILE_SIZE,
) -> dict:
    return {"file_path": file_path, "max_size": max_size}


def make_filelist_params(**kwargs) -> dict:
    return kwargs


def make_filelist_all_params(
    sort_by: str = EXPECTED_FILELIST_SORT_FIELDS[0],
    sort_order: str = EXPECTED_FILELIST_SORT_ORDERS[0],
    filter_ext: str = DEFAULT_FILELIST_FILTER_EXT,
    page: int = DEFAULT_PAGINATION_PAGE,
    limit: int = DEFAULT_PAGINATION_LIMIT,
) -> dict:
    return {
        "sort_by": sort_by,
        "sort_order": sort_order,
        "filter_ext": filter_ext,
        "page": page,
        "limit": limit,
    }


def make_file_data() -> list[dict]:
    return [
        {
            "name": f"{DEFAULT_FILELIST_FILE_BASE_NAME}.{DEFAULT_FILELIST_FILE_EXT}",
            "extension": DEFAULT_FILELIST_FILE_EXT,
            "size": DEFAULT_FILELIST_FILE_SIZE,
            "created_at": "2000-01-01T12:00:00",
        }
    ]

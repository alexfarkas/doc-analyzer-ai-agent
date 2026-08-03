from agent_enums import Role

from tests.consts.agent import DEFAULT_ROLE, DEFAULT_RESOURCES
from tests.factories.payloads.valid import (
    make_agent_config_block,
    make_doc_analyze_payload,
)


def make_doc_analyze_payload_without_mandatory_resources(
    role: Role | None = DEFAULT_ROLE,
    agents: list[dict] | None = None,
):
    """Payload for POST /doc/analyze without mandatory 'resources' field"""
    return {
        "role": role,
        "agents": agents or [make_agent_config_block()],
    }


def make_doc_analyze_payload_without_mandatory_role(
    resources: list[str] | None = None,
    agents: list[dict] | None = None,
):
    """Payload for POST /doc/analyze without mandatory 'role' field"""
    if resources is None:
        resources = DEFAULT_RESOURCES
    return {
        "resources": resources,
        "agents": agents or [make_agent_config_block()],
    }


def make_doc_analyze_payload_without_mandatory_agents(
    resources: list[str] | None = None,
    role: Role | None = DEFAULT_ROLE,
):
    """Payload for POST /doc/analyze without mandatory 'agents' field"""
    if resources is None:
        resources = DEFAULT_RESOURCES
    return {
        "resources": resources,
        "role": role,
    }


def make_doc_analyze_payload_with_invalid_role():
    """Payload for POST /doc/analyze with invalid 'role' field value"""
    return make_doc_analyze_payload(role="invalid role")


def make_doc_analyze_payload_with_empty_agents():
    """Payload for POST /doc/analyze with empty list in 'agents' field"""
    return make_doc_analyze_payload(agents=[])


def make_doc_analyze_payload_with_invalid_assignment():
    """Payload for POST /doc/analyze with invalid 'assignment' field value"""
    return make_doc_analyze_payload(
        agents=make_agent_config_block(assignment="invalid assignment")
    )

from agent_enums import Assignment


def start_event(agent_id: int, assignment: Assignment) -> tuple[str, dict]:
    return (
        "agent_start",
        {
            "agentId": agent_id,
            "agentType": assignment.value,
        }
    )


def stop_event(agent_id: int, assignment: Assignment) -> tuple[str, dict]:
    return (
        "agent_end",
        {
            "agentId": agent_id,
            "agentType": assignment.value,
        }
    )

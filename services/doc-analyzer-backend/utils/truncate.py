import json
from typing import Any


def truncate_value(
    value: Any,
    max_length: int = 100,
    suffix: str = "...",
) -> Any:
    if isinstance(value, str):
        if len(value) > max_length:
            return value[:max_length] + suffix
        return value

    if isinstance(value, dict):
        return {
            k: truncate_value(v, max_length, suffix) for k, v in value.items()
        }

    if isinstance(value, list):
        return [truncate_value(v, max_length, suffix) for v in value]

    if isinstance(value, tuple):
        return tuple(truncate_value(v, max_length, suffix) for v in value)

    if isinstance(value, (set, frozenset)):
        return type(value)(truncate_value(v, max_length, suffix) for v in value)

    return value


def format_data(
    data: Any,
    max_length: int = 100,
    indent: int = 2,
) -> str:
    truncated_data = truncate_value(data, max_length)
    try:
        return json.dumps(truncated_data, ensure_ascii=False, indent=indent)
    except (TypeError, ValueError):
        return repr(truncated_data)

import logging
from functools import lru_cache

import tiktoken
from langchain_core.messages import BaseMessage

from config.llm_config import LLMConfig
from llm.tokens.token_usage import TokenUsage, create_token_usage

logger = logging.getLogger(__name__)

LANGCHAIN_TO_OPENAI_ROLES = {
    "human": "user",
    "ai": "assistant",
    "system": "system",
    "tool": "tool",
}


@lru_cache(maxsize=32)
def get_encoder(model: str) -> tiktoken.Encoding:
    try:
        return tiktoken.encoding_for_model(model)
    except KeyError as e:
        logger.warning(
            f"Tiktoken encoder not found for {model}, using standard 'cl100k_base': {e}"
        )
        return tiktoken.get_encoding("cl100k_base")
    except Exception as e:
        logger.warning(
            f"Failed to get tiktoken encoder for {model}, using standard 'cl100k_base': {e}"
        )
        return tiktoken.get_encoding("cl100k_base")


async def calculate_stream_tokens_usage(text: str, model: str) -> int:
    try:
        encoder = get_encoder(model)
        return len(encoder.encode(text))
    except Exception:
        logger.warning(
            f"Failed to count stream tokens usage for {model}, rough estimation applied"
        )
        return max(1, len(text) // 4)


def calculate_tokens_usage(messages: list[BaseMessage], model: str) -> int:
    encoder = get_encoder(model)
    tokens = 0

    for msg in messages:
        role = LANGCHAIN_TO_OPENAI_ROLES[msg.type]

        content = getattr(msg, "content", "") or ""
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "")
                for block in content
                if isinstance(block, dict) and block.get("type") == "text"
            )

        # Формула OpenAI Chat API: <|im_start|>{role}\n{content}<|im_end|>\n
        tokens += 4  # <|im_start|>
        tokens += len(encoder.encode(role, disallowed_special=()))
        tokens += len(encoder.encode(content, disallowed_special=()))

        if hasattr(msg, "name") and msg.name:
            tokens += 1  # <|im_sep|>
            tokens += len(encoder.encode(msg.name, disallowed_special=()))

        tokens += 2  # <|im_end|>\n

    tokens += 3  # <|im_start|>assistant<|im_sep|> (префикс ответа)
    return max(tokens, 0)


def calculate_token_usage(
    messages: list[BaseMessage], llm_config: LLMConfig
) -> TokenUsage:
    token_usage = create_token_usage()

    for msg in messages:
        if msg.type != "ai" or not hasattr(msg, "response_metadata"):
            continue

        metadata = msg.response_metadata

        logger.info(f"Message: {metadata}")

        usage = _find_tokens_usage_block(metadata)

        if usage is None:
            logger.info(
                "Tokens usage not found in metadata, using tiktoken to calculate"
            )
            token_usage = create_token_usage(
                input_tokens=calculate_tokens_usage(messages, llm_config.model),
                output_tokens=calculate_tokens_usage(messages, llm_config.model),
            )
        else:
            token_usage.add_tokens(
                added_input_tokens=_count_input_tokens_usage(usage),
                added_output_tokens=_count_output_tokens_usage(usage),
            )

            if token_usage.any_tokens_eq_zero() and llm_config.provider == "ollama":
                logger.info(
                    "Unable to calculate tokens usage with metadata, using ollama format to calculate"
                )
                token_usage.add_tokens(
                    added_input_tokens=metadata.get("prompt_eval_count", 0),
                    added_output_tokens=metadata.get("eval_count", 0),
                )

            if token_usage.any_tokens_eq_zero():
                logger.info("Unable to calculate tokens, using tiktoken to calculate")
                token_usage = create_token_usage(
                    input_tokens=calculate_tokens_usage(messages, llm_config.model),
                    output_tokens=calculate_tokens_usage(messages, llm_config.model),
                )

    return token_usage


PRICING = {
    "ollama": {"input": 0.0, "output": 0.0},
    "openai": {"input": 0.15, "output": 0.60},
    "anthropic": {"input": 3.00, "output": 15.00},
}


def _find_tokens_usage_block(metadata: dict) -> dict | None:
    if "UsageMetadata" in metadata:
        return metadata["UsageMetadata"]
    # Нормализация LangChain и другими инструментами
    elif "token_usage" in metadata:
        return metadata["token_usage"]
    # Стандарт для большинства моделей
    elif "usage" in metadata:
        return metadata["usage"]
    else:
        return None


def _count_input_tokens_usage(usage: dict) -> int:
    # OpenAI
    if "prompt_tokens" in usage:
        return usage.get("prompt_tokens", 0)
    # Anthropic
    if "input_tokens" in usage:
        return usage.get("input_tokens", 0)
    else:
        return 0


def _count_output_tokens_usage(usage: dict) -> int:
    # OpenAI
    if "completion_tokens" in usage:
        return usage.get("completion_tokens", 0)
    # Anthropic
    if "output_tokens" in usage:
        return usage.get("output_tokens", 0)
    else:
        return 0


def calculate_cost(
    token_usage: TokenUsage, llm_config: LLMConfig, currency: str = "USD"
) -> float:
    provider = (
        llm_config.cost_calculation_provider
        if llm_config.cost_calculation_provider is not None
        else llm_config.provider
    )
    rates = PRICING.get(provider)
    cost = (
        token_usage.input_tokens * rates["input"] / 1_000_000
        + token_usage.output_tokens * rates["output"] / 1_000_000
    )
    return round(cost, 2) if currency == "USD" else round(cost * 100)

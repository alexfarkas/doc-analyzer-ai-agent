import logging

from src.doc_analyzer_backend.config.settings import app_settings
from src.doc_analyzer_backend.llm.tokens.token_usage import TokenUsage

logger = logging.getLogger(__name__)


MILLION_TOKENS = 1_000_000


def calculate_cost(
    token_usage: TokenUsage,
    provider: str,
    model: str,
    currency: str = "RUB",
) -> float:
    pricing = app_settings().pricing

    if provider == "ollama":
        logger.info(f"Local model is using, no price")
        return 0.0

    provider_pricing = pricing.providers[provider]
    if not provider_pricing:
        logger.warning(f"Pricing for provider {provider} not found")
        return 0.0

    model_pricing = provider_pricing[model]
    if not model_pricing:
        logger.warning(f"Pricing for model {model} (provider {provider}) not found")
        return 0.0

    input_price = model_pricing.input
    output_price = model_pricing.output
    logger.info(f"Pricing for model {provider}/{model} per 1M tokens: "
                f"input: {input_price}, output: {output_price}")

    total_input_price = token_usage.input_tokens * input_price / MILLION_TOKENS
    total_output_price = token_usage.output_tokens * output_price / MILLION_TOKENS

    cost = round(total_input_price + total_output_price, 2)

    logger.info(f"Tokens cost: {cost} {currency} "
                f"(input: {total_input_price}, output: {total_output_price})")
    return cost

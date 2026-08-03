from src.doc_analyzer_backend.agent.models.tokens.consumption_data import ConsumptionData
from src.doc_analyzer_backend.agent.models.tokens.token_usage import TokenUsage
from tests.consts.tokens import EXPECTED_TOKEN_USAGE, EXPECTED_ELAPSED, EXPECTED_COST


def make_token_usage(
    input_tokens: int = EXPECTED_TOKEN_USAGE["input_tokens"],
    output_tokens: int = EXPECTED_TOKEN_USAGE["output_tokens"],
) -> TokenUsage:
    return TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens)


def make_consumption_data(
    token_usage: TokenUsage = make_token_usage(),
    elapsed: float = EXPECTED_ELAPSED,
    cost: float = EXPECTED_COST,
) -> ConsumptionData:
    return ConsumptionData(token_usage=token_usage, elapsed=elapsed, cost=cost)

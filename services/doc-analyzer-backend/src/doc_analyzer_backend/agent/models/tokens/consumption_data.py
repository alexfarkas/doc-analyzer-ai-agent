from pydantic import BaseModel

from src.doc_analyzer_backend.agent.models.tokens.token_usage import TokenUsage, create_token_usage


class ConsumptionData(BaseModel):
    token_usage: TokenUsage | None = None
    elapsed: float= 0.0
    cost: float = 0.0

    def update_by_data(self, data: ConsumptionData):
        self.token_usage.add_usage(data.token_usage)
        self.elapsed += data.elapsed
        self.cost += data.cost

    def update(self, token_usage: TokenUsage, elapsed: float, cost: int):
        self.token_usage.add_usage(token_usage)
        self.elapsed += elapsed
        self.cost += cost


def create_consumption_data(
    token_usage: TokenUsage | None = None,
    elapsed: float = 0.0,
    cost: float = 0.0,
) -> ConsumptionData:
    if token_usage is None:
        token_usage = create_token_usage()
    return ConsumptionData(
        token_usage=token_usage,
        elapsed=elapsed,
        cost=cost,
    )

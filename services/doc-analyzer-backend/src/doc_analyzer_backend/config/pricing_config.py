from pydantic import BaseModel, Field


class PricingConfig(BaseModel):
    providers: dict[str, dict[str, ModelPricing]] = Field(
        default_factory=dict,
        description="LLM models pricing by providers",
    )


class ModelPricing(BaseModel):
    input: float = Field(ge=0, description="input tokens price")
    output: float = Field(ge=0, description="output tokens price")

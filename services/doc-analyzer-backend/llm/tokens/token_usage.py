from pydantic import BaseModel, computed_field


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int

    @computed_field
    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def add_usage(self, tokens: TokenUsage | None):
        if tokens:
            self.add_tokens(
                added_input_tokens=tokens.input_tokens,
                added_output_tokens=tokens.output_tokens,
            )

    def add_tokens(self, added_input_tokens: int, added_output_tokens: int):
        self.input_tokens += added_input_tokens
        self.output_tokens += added_output_tokens

    def any_tokens_eq_zero(self):
        return self.input_tokens == 0 or self.output_tokens == 0


def create_token_usage(input_tokens: int = 0, output_tokens: int = 0) -> TokenUsage:
    return TokenUsage(input_tokens=input_tokens, output_tokens=output_tokens)

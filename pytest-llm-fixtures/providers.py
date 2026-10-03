"""Translate two text-generation SDKs into the application model contract."""

import anthropic
import openai

from agent import InvalidDecision, ModelUnavailable


class OpenAITextModel:
    """Use a caller-owned OpenAI client with explicit timeout and retry policy."""

    def __init__(self, client: openai.OpenAI, model: str) -> None:
        self.client = client
        self.model = model

    def complete(self, *, instructions: str, prompt: str) -> str:
        """Accept completed text and translate transient provider failures."""
        try:
            response = self.client.with_options(
                max_retries=0, timeout=2.0
            ).responses.create(
                model=self.model,
                instructions=instructions,
                input=prompt,
            )
        except (openai.APITimeoutError, openai.RateLimitError) as exc:
            raise ModelUnavailable("Model request unavailable") from exc
        if response.status != "completed":
            raise InvalidDecision("Model response is not complete")
        text = response.output_text
        if not text.strip():
            raise InvalidDecision("Model response contains no text")
        return text


class AnthropicTextModel:
    """Use a caller-owned Anthropic client for complete text-only responses."""

    def __init__(self, client: anthropic.Anthropic, model: str) -> None:
        self.client = client
        self.model = model

    def complete(self, *, instructions: str, prompt: str) -> str:
        """Reject truncated/non-text output and translate transient failures."""
        try:
            response = self.client.with_options(
                max_retries=0, timeout=2.0
            ).messages.create(
                model=self.model,
                max_tokens=512,
                system=instructions,
                messages=[{"role": "user", "content": prompt}],
            )
        except (anthropic.APITimeoutError, anthropic.RateLimitError) as exc:
            raise ModelUnavailable("Model request unavailable") from exc
        if response.stop_reason != "end_turn":
            raise InvalidDecision("Model response is not complete")
        text = "".join(block.text for block in response.content if block.type == "text")
        if not text.strip():
            raise InvalidDecision("Model response contains no text")
        return text

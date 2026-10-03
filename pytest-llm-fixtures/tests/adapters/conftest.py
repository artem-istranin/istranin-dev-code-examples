"""Run real SDKs against synthetic responses without opening network sockets."""

from collections import deque
from contextlib import ExitStack

import anthropic
import httpx2
import openai
import pytest
from anthropic.types import Message
from openai.types.responses import Response

from providers import AnthropicTextModel, OpenAITextModel


@pytest.fixture(params=["openai", "anthropic"])
def provider(request):
    """Run the shared adapter contract against both supported providers."""
    return request.param


@pytest.fixture
def response_body(provider):
    """Build a fresh synthetic envelope validated against the installed SDK."""

    def make(text, *, complete=True, blocks=None):
        if provider == "openai":
            content = (
                blocks
                if blocks is not None
                else [{"type": "output_text", "text": text, "annotations": []}]
            )
            payload = {
                "id": "resp_test",
                "object": "response",
                "created_at": 0,
                "model": "offline-test-model",
                "status": "completed" if complete else "incomplete",
                "parallel_tool_calls": False,
                "tool_choice": "auto",
                "tools": [],
                "output": [
                    {
                        "id": "msg_test",
                        "type": "message",
                        "role": "assistant",
                        "status": "completed",
                        "content": content,
                    }
                ],
            }
            Response.model_validate(payload)
        else:
            content = blocks if blocks is not None else [{"type": "text", "text": text}]
            payload = {
                "id": "msg_test",
                "type": "message",
                "role": "assistant",
                "model": "offline-test-model",
                "content": content,
                "stop_reason": "end_turn" if complete else "max_tokens",
                "stop_sequence": None,
                "usage": {"input_tokens": 10, "output_tokens": 5},
            }
            Message.model_validate(payload)
        return payload

    return make


@pytest.fixture
def adapter_factory(provider):
    """Own each SDK client's lifetime and fail on unconfigured HTTP requests."""
    with ExitStack() as stack:

        def make(*outcomes):
            pending = deque(outcomes)
            requests = []

            def handle(request):
                requests.append(request)
                if not pending:
                    raise AssertionError("Unexpected extra provider request")
                outcome = pending.popleft()
                if isinstance(outcome, Exception):
                    raise outcome
                return outcome

            http_client = httpx2.Client(
                transport=httpx2.MockTransport(handle), trust_env=False
            )
            sdk_class, adapter_class = {
                "openai": (openai.OpenAI, OpenAITextModel),
                "anthropic": (anthropic.Anthropic, AnthropicTextModel),
            }[provider]
            client = stack.enter_context(
                sdk_class(
                    api_key="offline-test-key",
                    base_url=(
                        "https://provider.invalid/v1"
                        if provider == "openai"
                        else "https://provider.invalid"
                    ),
                    http_client=http_client,
                )
            )
            return adapter_class(client, model="offline-test-model"), requests

        yield make

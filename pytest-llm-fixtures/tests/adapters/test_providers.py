"""Check outgoing wire contracts and provider-to-application error translation."""

import json

import anthropic
import httpx2
import openai
import pytest

from agent import INSTRUCTIONS, InvalidDecision, ModelUnavailable, run_agent


def test_request_serialization_and_response_parsing(
    provider, response_body, adapter_factory
):
    output = '{"action":"answer","value":"Done"}'
    adapter, requests = adapter_factory(
        httpx2.Response(200, json=response_body(output))
    )

    assert adapter.complete(instructions="Return JSON", prompt="A question") == output

    assert len(requests) == 1
    request = requests[0]
    payload = json.loads(request.content)
    assert request.method == "POST"
    assert payload["model"] == "offline-test-model"
    if provider == "openai":
        assert request.url.path == "/v1/responses"
        assert payload["instructions"] == "Return JSON"
        assert payload["input"] == "A question"
    else:
        assert request.url.path == "/v1/messages"
        assert payload["system"] == "Return JSON"
        assert payload["messages"] == [{"role": "user", "content": "A question"}]
        assert payload["max_tokens"] == 512


@pytest.mark.parametrize("failure", ["timeout", "rate-limit"])
def test_transient_failures_are_translated_without_retries(failure, adapter_factory):
    outcome = (
        httpx2.ReadTimeout("synthetic timeout")
        if failure == "timeout"
        else httpx2.Response(
            429, json={"error": {"type": "rate_limit_error", "message": "busy"}}
        )
    )
    adapter, requests = adapter_factory(outcome)

    with pytest.raises(ModelUnavailable):
        adapter.complete(instructions="Return JSON", prompt="A question")
    assert len(requests) == 1


def test_authentication_errors_are_not_hidden_as_transient(provider, adapter_factory):
    adapter, requests = adapter_factory(
        httpx2.Response(
            401, json={"error": {"type": "authentication_error", "message": "bad key"}}
        )
    )
    error_type = (
        openai.AuthenticationError
        if provider == "openai"
        else anthropic.AuthenticationError
    )
    with pytest.raises(error_type):
        adapter.complete(instructions="Return JSON", prompt="A question")
    assert len(requests) == 1


def test_truncated_response_is_rejected(response_body, adapter_factory):
    adapter, _ = adapter_factory(
        httpx2.Response(200, json=response_body('{"action":', complete=False))
    )
    with pytest.raises(InvalidDecision, match="not complete"):
        adapter.complete(instructions="Return JSON", prompt="A question")


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_text_is_rejected(text, response_body, adapter_factory):
    adapter, _ = adapter_factory(httpx2.Response(200, json=response_body(text)))
    with pytest.raises(InvalidDecision, match="no text"):
        adapter.complete(instructions="Return JSON", prompt="A question")


def test_non_text_blocks_are_not_treated_as_answers(
    provider, response_body, adapter_factory
):
    blocks = (
        [{"type": "refusal", "refusal": "Cannot answer"}]
        if provider == "openai"
        else [{"type": "thinking", "thinking": "internal", "signature": "synthetic"}]
    )
    adapter, _ = adapter_factory(
        httpx2.Response(200, json=response_body("", blocks=blocks))
    )
    with pytest.raises(InvalidDecision, match="no text"):
        adapter.complete(instructions="Return JSON", prompt="A question")


def test_agent_and_real_adapter_work_together(
    provider, response_body, adapter_factory, mocker
):
    adapter, requests = adapter_factory(
        httpx2.Response(
            200, json=response_body('{"action":"search_docs","value":"refunds"}')
        ),
        httpx2.Response(
            200, json=response_body('{"action":"answer","value":"30 days"}')
        ),
    )
    search = mocker.Mock(return_value="Refund window: 30 days.")

    assert run_agent(adapter, search, "What is the refund window?") == "30 days"
    search.assert_called_once_with("refunds")
    assert len(requests) == 2
    body = json.loads(requests[1].content)
    if provider == "openai":
        prompt = body["input"]
        assert body["instructions"] == INSTRUCTIONS
    else:
        prompt = body["messages"][0]["content"]
        assert body["system"] == INSTRUCTIONS
    assert json.loads(prompt)["observations"] == [
        {"query": "refunds", "result": "Refund window: 30 days."}
    ]

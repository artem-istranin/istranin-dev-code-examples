"""Check outgoing wire contracts and provider-to-application error translation."""

import json

import anthropic
import httpx2
import openai
import pytest

from agent import Decision, InvalidDecision, ModelUnavailable, Observation, run_agent


def test_request_serialization_and_response_parsing(
    provider, response_body, adapter_factory
):
    output = '{"action":"answer","value":"Done"}'
    adapter, requests = adapter_factory(
        httpx2.Response(200, json=response_body(output))
    )

    observation = Observation("installation requirements", "Requires Python >=3.13.")
    decision = adapter.decide(
        question="Which Python version?", observations=(observation,)
    )

    assert decision == Decision(action="answer", value="Done")
    assert len(requests) == 1
    request = requests[0]
    payload = json.loads(request.content)
    assert request.method == "POST"
    assert payload["model"] == "offline-test-model"
    if provider == "openai":
        assert request.url.path == "/v1/responses"
        data = json.loads(payload["input"])
    else:
        assert request.url.path == "/v1/messages"
        assert payload["messages"][0]["role"] == "user"
        data = json.loads(payload["messages"][0]["content"])
        assert payload["max_tokens"] == 512
    assert data == {
        "question": "Which Python version?",
        "observations": [
            {"query": "installation requirements", "result": "Requires Python >=3.13."}
        ],
    }


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
        adapter.decide(question="A question", observations=())
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
        adapter.decide(question="A question", observations=())
    assert len(requests) == 1


def test_truncated_response_is_rejected(response_body, adapter_factory):
    adapter, _ = adapter_factory(
        httpx2.Response(200, json=response_body('{"action":', complete=False))
    )
    with pytest.raises(InvalidDecision, match="not complete"):
        adapter.decide(question="A question", observations=())


@pytest.mark.parametrize("text", ["", "   "])
def test_empty_text_is_rejected(text, response_body, adapter_factory):
    adapter, _ = adapter_factory(httpx2.Response(200, json=response_body(text)))
    with pytest.raises(InvalidDecision, match="no text"):
        adapter.decide(question="A question", observations=())


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
        adapter.decide(question="A question", observations=())


def test_agent_and_real_adapter_work_together(
    provider, response_body, adapter_factory, mocker
):
    adapter, requests = adapter_factory(
        httpx2.Response(
            200,
            json=response_body(
                '{"action":"search_docs","value":"installation requirements"}'
            ),
        ),
        httpx2.Response(
            200,
            json=response_body('{"action":"answer","value":"Python 3.13 or newer"}'),
        ),
    )
    search = mocker.Mock(return_value="Requires Python >=3.13.")

    assert (
        run_agent(adapter, search, "Which Python version do I need?")
        == "Python 3.13 or newer"
    )
    search.assert_called_once_with("installation requirements")
    assert len(requests) == 2
    body = json.loads(requests[1].content)
    if provider == "openai":
        prompt = body["input"]
    else:
        prompt = body["messages"][0]["content"]
    assert json.loads(prompt)["observations"] == [
        {"query": "installation requirements", "result": "Requires Python >=3.13."}
    ]


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param("not JSON", id="malformed-json"),
        pytest.param('{"action":"delete_account","value":"42"}', id="unknown-tool"),
        pytest.param('{"action":"search_docs","value":12}', id="wrong-argument-type"),
        pytest.param('{"action":"search_docs","value":" "}', id="empty-query"),
        pytest.param('{"action":"answer"}', id="missing-value"),
        pytest.param('{"action":"answer","value":"ok","extra":true}', id="extra-field"),
    ],
)
def test_invalid_decisions_never_reach_tools(
    raw, response_body, adapter_factory, mocker
):
    adapter, requests = adapter_factory(httpx2.Response(200, json=response_body(raw)))
    search = mocker.Mock()

    with pytest.raises(InvalidDecision):
        run_agent(adapter, search, "Which Python version?")

    search.assert_not_called()
    assert len(requests) == 1

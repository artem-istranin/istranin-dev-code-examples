"""Protect agent outcomes, tool restrictions, failure policy, and fresh state."""

import json

import pytest

from agent import INSTRUCTIONS, InvalidDecision, ModelUnavailable, StepLimitExceeded


def test_search_result_reaches_next_turn(llm_script, search_tool, agent_factory):
    model = llm_script(
        '{"action":"search_docs","value":"refund policy"}',
        '{"action":"answer","value":"Refunds are available for 30 days."}',
    )
    search_tool.return_value = "Refund window: 30 days."
    ask = agent_factory(model)

    assert ask("Can I request a refund?") == "Refunds are available for 30 days."
    search_tool.assert_called_once_with("refund policy")
    second_prompt = json.loads(model.complete.call_args_list[1].kwargs["prompt"])
    assert second_prompt["observations"] == [
        {"query": "refund policy", "result": "Refund window: 30 days."}
    ]
    assert model.complete.call_count == 2


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
def test_invalid_decisions_never_call_tools(
    raw, llm_script, search_tool, agent_factory
):
    ask = agent_factory(llm_script(raw))

    with pytest.raises(InvalidDecision):
        ask("Find the refund policy")
    search_tool.assert_not_called()


def test_budget_stops_before_another_tool_call(llm_script, search_tool, agent_factory):
    search = '{"action":"search_docs","value":"refund policy"}'
    model = llm_script(search, search)
    search_tool.return_value = "No matching document."
    ask = agent_factory(model, max_steps=2)

    with pytest.raises(StepLimitExceeded):
        ask("Find the refund policy")
    assert model.complete.call_count == 2
    search_tool.assert_called_once_with("refund policy")


def test_invalid_budget_does_no_work(llm_script, search_tool, agent_factory):
    model = llm_script()
    with pytest.raises(ValueError, match="max_steps"):
        agent_factory(model, max_steps=0)("Hello")
    model.complete.assert_not_called()
    search_tool.assert_not_called()


def test_model_failure_stops_without_retry(llm_script, search_tool, agent_factory):
    model = llm_script(ModelUnavailable("busy"))
    with pytest.raises(ModelUnavailable):
        agent_factory(model)("Find the refund policy")
    assert model.complete.call_count == 1
    search_tool.assert_not_called()


def test_tool_failure_stops_before_another_model_turn(
    llm_script, search_tool, agent_factory
):
    model = llm_script('{"action":"search_docs","value":"refund policy"}')
    search_tool.side_effect = TimeoutError("search unavailable")

    with pytest.raises(TimeoutError):
        agent_factory(model)("Find the refund policy")
    assert model.complete.call_count == 1
    search_tool.assert_called_once_with("refund policy")


@pytest.mark.parametrize(
    "instructions",
    [INSTRUCTIONS, INSTRUCTIONS + " Keep the answer to one sentence."],
    ids=["standard", "concise"],
)
@pytest.mark.parametrize(
    "question", ["How do refunds work?", "Can I get my money back?"]
)
def test_prompt_variants_preserve_the_request_contract(
    instructions, question, llm_script, search_tool, agent_factory
):
    model = llm_script('{"action":"answer","value":"See the refund policy."}')

    result = agent_factory(model, instructions=instructions)(question)

    assert result == "See the refund policy."
    request = model.complete.call_args.kwargs
    assert request["instructions"] == instructions
    assert json.loads(request["prompt"]) == {"question": question, "observations": []}
    search_tool.assert_not_called()


def test_reusing_agent_does_not_leak_conversation(
    llm_script, search_tool, agent_factory
):
    model = llm_script(
        '{"action":"search_docs","value":"private draft"}',
        '{"action":"answer","value":"First answer"}',
        '{"action":"answer","value":"Second answer"}',
    )
    search_tool.return_value = "First request's search result"
    ask = agent_factory(model)

    assert ask("First question") == "First answer"
    assert ask("Second question") == "Second answer"
    last_prompt = json.loads(model.complete.call_args.kwargs["prompt"])
    assert last_prompt == {"question": "Second question", "observations": []}

"""Protect tool dispatch, returned answers, failure handling, and isolation."""

import pytest

from agent import Decision, ModelUnavailable, Observation, StepLimitExceeded, run_agent


def test_direct_answer_does_not_search(model_script, search_tool):
    model = model_script(Decision(action="answer", value="Hello!"))

    result = run_agent(model, search_tool, "Hello")

    assert result == "Hello!"
    model.decide.assert_called_once_with(question="Hello", observations=())
    search_tool.assert_not_called()


def test_search_then_answer(model_script, search_tool, mocker):
    model = model_script(
        Decision(action="search_docs", value="installation requirements"),
        Decision(action="answer", value="Use Python 3.13 or newer."),
    )
    search_tool.return_value = "Requires Python >=3.13."
    question = "Which Python version do I need?"

    result = run_agent(model, search_tool, question)

    assert result == "Use Python 3.13 or newer."
    search_tool.assert_called_once_with("installation requirements")
    assert model.decide.call_args_list == [
        mocker.call(question=question, observations=()),
        mocker.call(
            question=question,
            observations=(
                Observation("installation requirements", "Requires Python >=3.13."),
            ),
        ),
    ]


def test_budget_stops_before_another_tool_call(model_script, search_tool):
    search = Decision(action="search_docs", value="installation requirements")
    model = model_script(search, search)
    search_tool.return_value = "No matching document."

    with pytest.raises(StepLimitExceeded):
        run_agent(model, search_tool, "Which Python version?", max_steps=2)

    assert model.decide.call_count == 2
    search_tool.assert_called_once_with("installation requirements")


def test_invalid_budget_does_no_work(model_script, search_tool):
    model = model_script()
    with pytest.raises(ValueError, match="max_steps"):
        run_agent(model, search_tool, "Hello", max_steps=0)
    model.decide.assert_not_called()
    search_tool.assert_not_called()


def test_model_failure_stops_without_retry(model_script, search_tool):
    model = model_script(ModelUnavailable("busy"))

    with pytest.raises(ModelUnavailable):
        run_agent(model, search_tool, "Which Python version?")

    assert model.decide.call_count == 1
    search_tool.assert_not_called()


def test_tool_failure_stops_before_another_model_turn(model_script, search_tool):
    model = model_script(
        Decision(action="search_docs", value="installation requirements")
    )
    search_tool.side_effect = TimeoutError("search unavailable")

    with pytest.raises(TimeoutError):
        run_agent(model, search_tool, "Which Python version?")

    assert model.decide.call_count == 1
    search_tool.assert_called_once_with("installation requirements")


def test_requests_do_not_share_search_results(model_script, search_tool):
    model = model_script(
        Decision(action="search_docs", value="private draft"),
        Decision(action="answer", value="First answer"),
        Decision(action="answer", value="Second answer"),
    )
    search_tool.return_value = "First request's search result"

    assert run_agent(model, search_tool, "First question") == "First answer"
    assert run_agent(model, search_tool, "Second question") == "Second answer"

    model.decide.assert_called_with(question="Second question", observations=())

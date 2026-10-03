"""Named fixture factories for agent scenarios, scoped to one test item."""

import pytest

from agent import TextModel, run_agent


def search_docs(query: str) -> str:
    """Describe the external search signature for autospecced test doubles."""
    raise NotImplementedError


@pytest.fixture
def llm_script(mocker):
    """Create a model whose successive calls return text or raise exceptions."""

    def make(*outcomes):
        model = mocker.create_autospec(TextModel, instance=True, spec_set=True)
        model.complete.side_effect = outcomes
        return model

    return make


@pytest.fixture
def search_tool(mocker):
    """Give each case a new autospecced external search boundary."""
    return mocker.create_autospec(search_docs, spec_set=True)


@pytest.fixture
def agent_factory(search_tool):
    """Compose the real agent with explicit model and shared per-test search."""

    def make(model, **options):
        def ask(question):
            return run_agent(model, search_tool, question, **options)

        return ask

    return make

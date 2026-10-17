"""Fresh model scripts and search mocks for each agent test."""

import pytest

from agent import DecisionModel


@pytest.fixture
def model_script(mocker):
    """Create a model that returns decisions or raises configured exceptions."""

    def make(*outcomes):
        model = mocker.create_autospec(DecisionModel, instance=True, spec_set=True)
        model.decide.side_effect = outcomes
        return model

    return make


@pytest.fixture
def search_tool(mocker):
    """Provide the search(query) -> text signature without a search service."""

    def search_docs(query: str) -> str:
        raise NotImplementedError

    return mocker.create_autospec(search_docs, spec_set=True)

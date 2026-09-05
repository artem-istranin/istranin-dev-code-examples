# LangGraph agent testing with pytest

This is the runnable companion project for the istranin.dev article
"How to Test a LangGraph Agent with pytest (Without API Calls)."

It demonstrates how to:

- run a compiled LangGraph `StateGraph` with scripted model responses;
- mock an external tool dependency with pytest-mock;
- assert the tool input, `ToolMessage`, and final graph response;
- protect an explicit timeout policy without making network requests.

## Project files

```text
langgraph-agent-testing/
├── agent.py
├── test_agent.py
├── pyproject.toml
└── uv.lock
```

## Run the tests

Install the exact locked dependencies and execute the test suite:

```bash
uv sync --locked
uv run pytest test_agent.py -v
```

The suite runs two deterministic tests. It does not need a model API key or an external order service.

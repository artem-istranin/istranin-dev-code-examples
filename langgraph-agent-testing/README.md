[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# LangGraph agent testing with pytest

> **Companion article:**
> [How to Test a LangGraph Agent with pytest (Without API Calls)](https://istranin.dev/blog/test-langgraph-agent-pytest/)
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## Overview

It demonstrates how to:

- run a compiled LangGraph `StateGraph` with scripted model responses;
- mock an external tool dependency with pytest-mock;
- assert the tool input, `ToolMessage`, its delivery to the next model turn, and final graph response;
- protect an explicit timeout policy without making network requests.

## Requirements

- Python 3.13 or newer.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for the locked dependencies.

## Run the example

From the `langgraph-agent-testing/` directory, install the locked dependencies and run:

```bash
uv sync --locked
uv run pytest test_agent.py -v
```

The suite runs two deterministic tests. It does not need a model API key or an external order service.

## Project files

```text
langgraph-agent-testing/
├── agent.py
├── test_agent.py
├── pyproject.toml
└── uv.lock
```

---

[All examples](../README.md#article-examples) · [istranin.dev](https://istranin.dev/) · [Apache-2.0 license](../LICENSE)

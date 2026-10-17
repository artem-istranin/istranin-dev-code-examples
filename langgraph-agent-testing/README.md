[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# LangGraph agent testing with pytest

> **Companion article:**
> [How to Test a LangGraph Agent with pytest (Without API Calls)](https://istranin.dev/blog/test-langgraph-agent-pytest/)
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## Overview

It demonstrates how to:

- run a compiled LangGraph `StateGraph` with scripted model responses;
- mock an external tool dependency with pytest-mock;
- use fresh fixtures and parametrized cases to check both routing branches;
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

The suite runs 4 deterministic cases: a direct answer, 2 parametrized order lookups, and a service timeout. It does not need a model API key or an external order service.

## Test patterns

`model_script` supplies real `AIMessage` values through a mocked model. It returns the
model passed to `build_agent` and the tool-bound model whose `invoke` calls the tests
inspect. `order_client` provides a fresh autospecced service mock for each test case.

The application graph stays unchanged: the real model node, `tools_condition`, and
`ToolNode` process those messages. The example checks direct completion, a tool result
reaching the next model turn, and a timeout stopping the graph without a second model
call. It does not test a live model's tool choice or answer quality.

To observe a routing regression, temporarily remove
`builder.add_edge("tools", "model")` from `agent.py` and run:

```bash
uv run pytest test_agent.py -k tool_result_reaches_next_turn -v
```

Both cases fail because the model runs only once. Restore the edge and run the full
suite again; all 4 cases should pass.

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

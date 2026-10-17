[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# Unit testing AI agents with pytest

> **Companion article:**
> [Pytest Fixtures and Mocking for AI Agents and LLM Apps](https://istranin.dev/blog/pytest-fixtures-mocking-llm-agents/)
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## Overview

Run a small documentation-search agent with scripted model decisions and a mocked search
tool. Test tool dispatch, returned answers, failures, and call limits without model randomness,
API keys, or token costs. Separately test real OpenAI and Anthropic SDK adapters against
synthetic HTTP responses. The default test suite blocks Python sockets and needs no
provider account, real model, API key, or external search service.

The example separates three questions:

| Layer | What runs | What the test establishes |
| --- | --- | --- |
| Agent behavior | Real agent loop, scripted decisions, mocked search | Tool arguments, observation propagation, failure handling, step limit, fresh state |
| SDK adapter | Real adapter and SDK, local `httpx2.MockTransport` | Request data, decision validation, incomplete output and error translation |
| Live checks and evaluations | Not part of this offline example | Provider compatibility and model quality require separate, credentialed checks |

The provider adapters parse application-owned JSON with `action` and `value` fields into a
validated `Decision`. The agent sees that typed decision, not the JSON or SDK response.
It is **not** either provider's native tool-calling protocol. The allowlist contains only
`search_docs` and `answer`; validation happens before tool execution. The search boundary is
read-only. Adding a write tool requires authorization and idempotency requirements beyond this
example. The prompt is not a security boundary.

## Requirements

- Python 3.13 and [uv](https://docs.astral.sh/uv/getting-started/installation/).
- Package download access for the initial `uv sync --locked`.

The lockfile contains pytest 9.1.1, pytest-mock 3.16.0, OpenAI 3.24.0, Anthropic 1.11.0,
HTTPX2 2.13.1, and Pydantic 2.13.5. These SDK releases use `httpx2`. Older SDK releases may
use `httpx`; match the transport to the SDK you actually install.

## Run the example

From this directory:

```bash
uv sync --locked
./scripts/check
```

Expected: formatting and lint checks pass, **38 tests pass**, and the application modules
`agent.py` and `providers.py` have 100% statement and branch coverage. This is coverage of
the example's Python behavior, not a measurement of model quality.

Run one layer or inspect the fixtures:

```bash
uv run --locked pytest tests/unit -v
uv run --locked pytest tests/adapters -v
uv run --locked pytest tests/unit/test_agent.py --fixtures-per-test
```

`scripts/check` runs the same command in GitHub Actions. Tests use dummy credentials and
the deliberately non-routable `provider.invalid` host. `offline-test-model` is a synthetic
identifier checked by the local transport; it is not a real provider model recommendation.

## Project files

```text
pytest-llm-fixtures/
  agent.py                       Decision and observation types, model port, bounded loop
  providers.py                   OpenAI Responses and Anthropic Messages adapters
  tests/
    conftest.py                  Remove ambient provider credentials
    test_offline_policy.py       Check the suite's socket and credential policy
    unit/
      conftest.py                model_script, search_tool
      test_agent.py              Tool dispatch, answers, failures, budgets, fresh state
    adapters/
      conftest.py                provider, response_body, adapter_factory
      test_providers.py          SDK wire contracts and agent/adapter composition
  scripts/check                 Format, lint, tests, coverage gate
  pyproject.toml
  uv.lock
```

## Fixture architecture

`model_script(*outcomes)` creates an autospecced `DecisionModel`; each call returns the next
`Decision` or raises the next exception. Exhausting the script fails instead of returning
an invented default. `search_tool` is a fresh autospecced mock. Tests pass both directly to
`run_agent`. Every fixture uses function scope.

`DecisionModel.decide(question=..., observations=...)` returns an application-owned decision.
Immutable observations carry search queries and results between turns. Prompt construction
and JSON validation belong to `providers.py`, outside the agent loop. Tests assert structured
inputs and outputs, not exact system-prompt wording.

Provider details stay in `tests/adapters/conftest.py`. The parametrized `provider` fixture
runs the same contract against both SDKs. `response_body` validates each synthetic envelope
against the installed SDK's response model. `adapter_factory` owns SDK clients with an
`ExitStack`, records requests, and rejects any call without a scripted response.

The suite checks success, malformed JSON, unknown actions, invalid arguments, empty and
truncated text, timeout and 429 translation, authentication error propagation, tool failures,
and repeated searches. Each call to the agent starts a fresh conversation. The adapter suite
also checks that invalid provider decisions cannot reach a tool.

## Failure policy and limits

- Adapters explicitly disable SDK retries and set a two-second request timeout. Timeout
  tests raise transport exceptions immediately; they do not wait two seconds.
- Rate limits and timeouts become `ModelUnavailable`. Authentication errors retain their
  SDK exception type. Other provider errors propagate.
- The agent does not retry model or search failures. Its default budget is three model
  calls. It cannot execute a search after the final allowed call because there is no
  remaining turn to consume the result.
- A step limit does not bound elapsed time or token cost. A production search adapter
  still needs its own timeout, and an overall deadline may be necessary.
- SDK parsing of synthetic responses does not establish compatibility with the live
  provider. No live API, async client, native tool-calling, or streaming check is included.
- `pytest-socket` is an in-process guard, not an operating-system sandbox. Subprocesses,
  native transports, and separate workers need their own network policy.

Add unit cases when the application gains a new action or failure policy. Live integration
checks establish current provider compatibility; evaluations measure the quality of actual
model decisions and answers. Neither belongs in the default offline test run.

## Sources and related reading

- [Testing a LangGraph agent](https://istranin.dev/blog/test-langgraph-agent-pytest/)
- [Pytest fixture architecture and parametrization](https://istranin.dev/blog/pytest-fixtures-parametrization-scalable-tests/)
- [Pytest fixture documentation](https://docs.pytest.org/en/stable/how-to/fixtures.html)
- [OpenAI Python SDK](https://github.com/openai/openai-python)
- [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python)
- [HTTPX2 mock transports](https://pydantic.dev/docs/httpx2/advanced/transports/#mock-transports)
- [pytest-socket](https://github.com/miketheman/pytest-socket)

---

[All examples](../README.md#article-examples) · [istranin.dev](https://istranin.dev/) · [Apache-2.0 license](../LICENSE)

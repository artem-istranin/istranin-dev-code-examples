[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# Pytest fixtures and mocking for AI agents

> **Companion article:** Pytest Fixtures and Mocking for AI Agents and LLM Apps
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## Overview

Run a small documentation-search agent with controlled model responses. Reuse named fixtures
without sharing mutable conversation state, then test real OpenAI and Anthropic SDK adapters
against synthetic HTTP responses. The default test suite blocks Python sockets and needs no
provider account, real model, API key, or external search service.

The example separates three questions:

| Layer | What runs | What the test establishes |
| --- | --- | --- |
| Agent behavior | Real validation and orchestration, scripted model, mocked search | Tool arguments, observation propagation, failure handling, step limit, fresh state |
| SDK adapter | Real adapter and SDK, local `httpx2.MockTransport` | Request path and payload, text parsing, incomplete output and error translation |
| Live checks and evaluations | Not part of this offline example | Provider compatibility and model quality require separate, credentialed checks |

The action protocol is deliberately application-owned JSON with `action` and `value` fields.
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

Expected: formatting and lint checks pass, **35 tests pass**, and the application modules
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
  agent.py                       Model port, validated decisions, bounded loop
  providers.py                   OpenAI Responses and Anthropic Messages adapters
  tests/
    conftest.py                  Remove ambient provider credentials
    test_offline_policy.py       Check the suite's socket and credential policy
    unit/
      conftest.py                llm_script, search_tool, agent_factory
      test_agent.py              Agent behavior and prompt construction cases
    adapters/
      conftest.py                provider, response_body, adapter_factory
      test_providers.py          SDK wire contracts and agent/adapter composition
  scripts/check                 Format, lint, tests, coverage gate
  pyproject.toml
  uv.lock
```

## Fixture architecture

`llm_script(*outcomes)` creates an autospecced `TextModel`; each call returns the next
string or raises the next exception. Exhausting the script fails instead of returning
an invented default. `search_tool` is a fresh autospecced mock. `agent_factory` composes
them with the real `run_agent` function. Every fixture uses function scope.

Provider details stay in `tests/adapters/conftest.py`. The parametrized `provider` fixture
runs the same contract against both SDKs. `response_body` validates each synthetic envelope
against the installed SDK's response model. `adapter_factory` owns SDK clients with an
`ExitStack`, records requests, and rejects any call without a scripted response.

The suite checks success, malformed JSON, unknown actions, invalid arguments, empty and
truncated text, timeout and 429 translation, authentication error propagation, tool failures,
and repeated searches. Reusing an agent starts a fresh conversation. Prompt variants check
that instructions and input reach the model boundary; they do not score real answers.

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

Try changing an action to an unsupported tool, removing observation propagation, or enabling
SDK retries. The corresponding behavior test should fail. Add evaluation cases separately
when you need to compare actual prompt quality.

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

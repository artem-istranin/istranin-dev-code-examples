[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# Pytest hooks examples

> **Companion article:**
> [Pytest Hooks Tutorial: 5 Practical Examples for Python Tests](https://istranin.dev/blog/pytest-hooks-examples/)
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## Overview

This self-contained project demonstrates five pytest hook functions in one small local plugin:

- `pytest_addoption` adds an `--env` command-line option;
- `pytest_configure` registers a custom marker;
- `pytest_collection_modifyitems` skips tests for other environments;
- `pytest_runtest_makereport` records failed test calls through a hook wrapper;
- `pytest_terminal_summary` prints a compact list for failure triage.

The examples target developers who already know how to write and run ordinary pytest tests.

## Requirements

- Python 3.13 or newer.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for the locked dependencies.

## Run the example

From the `pytest-hooks-examples/` directory, install the locked dependencies and run:

```bash
uv sync --locked
uv run pytest -q
```

The result is two passing tests and one skipped staging test. Select the staging environment to run
all three tests:

```bash
uv run pytest -q --env=staging
```

## Project files

```text
pytest-hooks-examples/
├── checkout.py
├── conftest.py
├── failure_example.py
├── test_checkout.py
├── test_hooks.py
├── pyproject.toml
└── uv.lock
```

## See the failure summary

`failure_example.py` fails deliberately and is not part of normal test discovery. Run it explicitly
to see the custom summary:

```bash
uv run pytest failure_example.py -q
```

The command exits with status 1, as a real test failure should, and ends with:

```text
=========================== failed tests for triage ============================
failure_example.py::test_inventory_count
```

---

[All examples](../README.md#article-examples) · [istranin.dev](https://istranin.dev/) · [Apache-2.0 license](../LICENSE)

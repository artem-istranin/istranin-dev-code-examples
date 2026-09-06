# Pytest hooks examples

This self-contained project demonstrates five pytest hook functions in one small local plugin:

- `pytest_addoption` adds an `--env` command-line option;
- `pytest_configure` registers a custom marker;
- `pytest_collection_modifyitems` skips tests for other environments;
- `pytest_runtest_makereport` records failed test calls through a hook wrapper;
- `pytest_terminal_summary` prints a compact list for failure triage.

The examples target developers who already know how to write and run ordinary pytest tests.

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

## Run the suite

Install the locked dependencies and run the default local environment:

```bash
uv sync --locked
uv run pytest -q
```

The result is two passing tests and one skipped staging test. Select the staging environment to run
all three tests:

```bash
uv run pytest -q --env=staging
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

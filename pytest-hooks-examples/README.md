[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# Pytest hooks examples

> **Companion article:**
> [Pytest Hooks Tutorial: Select Tests and Rerun Failures](https://istranin.dev/blog/pytest-hooks-examples/)
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## What this example solves

Choose which checkout checks to run with `--env`, then get a copyable command
for rerunning failures in the same environment. The tests stay focused on the
application; a small plugin in `conftest.py` handles selection and reporting.

These are offline demonstration tests. Selecting `staging` changes test
selection, not network endpoints or credentials.

## Requirements

- Python 3.13 or newer.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for the locked dependencies.
- A POSIX shell such as Bash or Zsh for the printed rerun command.

## Select the checkout checks

From the `pytest-hooks-examples/` directory, install the locked dependencies and run:

```bash
uv sync --locked
uv run pytest test_checkout.py -q -rs
```

The result is **1 passed, 1 skipped**. The skipped check requires staging.
Choose that environment to run both checks:

```bash
uv run pytest test_checkout.py -q --env=staging
```

The result is **2 passed**.

Use `@pytest.mark.env('local')` or `@pytest.mark.env('staging')` to restrict a test
to one environment. Unmarked tests run in either environment. Invalid markers
stop the run with a usage error naming the affected test.

## See the custom report

`failure_example.py` has a deliberately failing staging inventory check. It is
excluded from normal test discovery. Request it alongside the passing checks:

```bash
uv run pytest test_checkout.py failure_example.py -q --env=staging
```

The result is **1 failed, 2 passed**, with exit status `1`. After the assertion
details, the plugin adds:

```text
====================== 🛒 CHECKOUT CHECK: STAGING =======================
❌ Tests needing attention: 1
🔁 Rerun just these tests:
uv run pytest --env=staging -q failure_example.py::test_inventory_count
```

Copy that command to rerun only the inventory check, keeping `--env=staging`.
To complete the exercise, change `inventory_count()` in `failure_example.py`
to return `3` and run the command again. The result becomes **1 passed**, and
the custom failure block disappears.

The report includes test-body, setup, and cleanup failures, with each test
listed once. It targets ordinary runs in one pytest process; distributed
`pytest-xdist` runs would need result aggregation from workers.

## How the hooks support the workflow

- `pytest_addoption` adds `--env`.
- `pytest_configure` registers the environment marker.
- `pytest_collection_modifyitems` skips tests for other environments.
- `pytest_runtest_makereport` remembers tests with failures.
- `pytest_terminal_summary` prints the rerun command.

## Verify the plugin

`test_hooks.py` checks environment selection, invalid markers, fixture failures,
and rerunning only the failed test IDs, including names that need shell quoting.
Run the demonstration tests and plugin tests together:

```bash
uv run pytest -q
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

---

[All examples](../README.md#article-examples) · [istranin.dev](https://istranin.dev/) · [Apache-2.0 license](../LICENSE)

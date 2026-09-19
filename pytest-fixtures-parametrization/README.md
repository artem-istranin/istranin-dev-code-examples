# Pytest fixtures and parametrization

A self-contained example of fixture architecture for a growing test suite. The
SQLite inventory contract runs against memory and temporary-file storage, with
fresh mutable state for every test item.

Requires uv and Python 3.13 or later. `.python-version` selects Python 3.13; the
lockfile pins pytest 9.1.1 and pytest-xdist 3.8.0.

## Run the examples

```bash
uv sync --locked
uv run pytest -q
uv run pytest tests -n 2 -q
```

Both commands run 32 test items. The suite protects successful reservations,
stock exhaustion, invalid quantities, unchanged state after rejected operations,
independent products, and opening balances. Memory and file-backed SQLite are
storage configurations, not substitutes for testing another production database.

Inspect the product of two storage configurations and three quantity rows:

```bash
uv run pytest tests/test_reservations.py::test_reserve --collect-only -q
uv run pytest 'tests/test_reservations.py::test_reserve[file-exhaust-stock]' -q
uv run pytest tests/test_reservations.py::test_reserve --setup-plan -q
uv run pytest --durations=20 --durations-min=0 -q
```

## Examples by responsibility

| Files | What they demonstrate |
| --- | --- |
| `refactoring/before.py`, `refactoring/after.py` | Three equivalent cases before and after extracting setup and parametrizing behavior |
| `tests/conftest.py` | Connection ownership, fixture composition, factories, indirect setup, and collection hooks |
| `tests/test_reservations.py` | Input rows and rejection contracts across two storage configurations |
| `tests/test_products.py` | A factory creates multiple products inside a scenario |
| `tests/test_prepared.py` | Case rows configure setup using selective indirect parametrization |
| `tests/test_dynamic.py` | CLI-driven cases with validation, defaults, deduplication, and stable ordering |
| `benchmarks/` | A serial experiment isolating the cost of repeating immutable setup |

The refactoring alternatives are excluded from normal discovery. Run both with:

```bash
uv run pytest refactoring/before.py refactoring/after.py -q
```

That produces six passing items: three cases in each alternative.

Select two opening balances for the dynamic example:

```bash
uv run pytest tests/test_dynamic.py --opening-stock=3 --opening-stock=8 -q
```

This produces four items after storage parametrization. Repeated values are
deduplicated and sorted. With no options the balances are 1 and 5. Values below 1
produce a collection error; `empty_parameter_set_mark = "fail_at_collect"` also
rejects empty parametrizations if the collection source is extended later.

## Fixture ownership

```text
connection [memory or file; fresh for each test item]
  -> inventory
       -> stocked_inventory -> reservation tests
       -> make_product      -> multi-product scenarios
       -> prepared_inventory -> indirect setup cases
       -> dynamic test      -> CLI-derived opening balance

after the test item: close its connection
```

The application uses SQLite autocommit. It does not implement transaction rollback
isolation or share a connection between tests. The connection owner explicitly
closes it using `contextlib.closing`.

## Scope experiment

```bash
uv run pytest benchmarks -q --catalog-scope=function
uv run pytest benchmarks -q --catalog-scope=session
```

Each run executes ten test items. Function scope performs ten catalog setups;
session scope performs one. Each setup deliberately sleeps for 0.1 seconds and
returns an immutable tuple. The terminal summary reports setup count and elapsed
time inside the fixture.

This is a controlled demonstration of reusing fixed-cost setup. It is not a
production benchmark or a claim of a universal suite speedup. Timing depends on
the machine and scheduling. Run this experiment serially: its timing summary is
local to the pytest process and does not aggregate xdist workers.

## Validation

Run the same commands used in CI:

```bash
sh scripts/check
```

The script runs serial and parallel tests, custom dynamic cases, the refactoring
alternatives, and both scope experiments. No external services or credentials are
required. The illustrative application is intentionally small; it does not model
a production inventory system's full transaction or concurrency requirements.

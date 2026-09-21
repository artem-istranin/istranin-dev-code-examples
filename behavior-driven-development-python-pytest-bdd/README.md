# Behavior-driven development in Python with pytest-bdd

Continue the seat-reservation example from
[Test-Driven Development in Python with pytest](https://istranin.dev/blog/test-driven-development-python-pytest/).
The `Inventory` implementation and four original pytest cases are preserved. Gherkin scenarios make
the same rules reviewable as concrete customer outcomes and add examples for selling the last seats,
an empty inventory, and a valid request after an earlier rejection.

## Run the example

Requires Python 3.13 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/).
From this directory:

```bash
uv sync --locked
uv run pytest -v
```

The locked environment uses pytest 8.4.2 and pytest-bdd 8.1.0. Pytest stays below 9 in this standalone
example to avoid the fixture-registration deprecation warnings that pytest-bdd 8.1.0 produces with
pytest 9.1.1. The original TDD project keeps its own dependencies.

The complete suite has **11 passing cases**: four original pytest cases and seven BDD cases.
Run either group separately:

```bash
uv run pytest tests/test_inventory.py -v
uv run pytest tests/test_reservations.py -v
```

## Project files

```text
behavior-driven-development-python-pytest-bdd/
  inventory.py
  tests/
    features/
      reservations.feature
    test_inventory.py
    test_reservations.py
  pyproject.toml
  uv.lock
```

## Agree on examples before automating them

A useful discovery conversation includes product, development, and testing perspectives. Start with
the rule "customers can reserve available seats" and ask what should happen at its boundaries.

| Available | Requested | Outcome | Remaining |
| --- | --- | --- | --- |
| 3 | 2 | Accept | 1 |
| 3 | 3 | Accept the last seats | 0 |
| 2 | 3 | Reject: not enough seats | 2 |
| 0 | 1 | Reject: not enough seats | 0 |
| 3 | 0 | Reject: quantity must be positive | 3 |
| 3 | -1 | Reject: quantity must be positive | 3 |

The final scenario makes a sequence explicit: reserve two of three seats, reject a request for two
more, then accept a request for the last seat. Rejection must preserve availability for the next
customer. Each scenario gets a fresh inventory; only steps inside that scenario share state.

`Scenario Outline` expands each Examples row into a pytest case. The Given step returns an
`Inventory` through `target_fixture`. The When step calls `reserve` and exposes the expected domain
exception, or `None` on success. Then steps check the outcome and remaining availability. Unexpected
exceptions are not caught.

These scenarios already pass against the completed TDD implementation. Adding executable
specifications to existing behavior is useful, but it does not demonstrate a new red-green cycle.
For a future rule, agree on an example first, observe its behavioral failure, implement the rule
through small TDD steps, and run both groups again.

## What the example proves

The scenarios exercise the real public domain operation in memory. They do not launch a browser or
test an HTTP API, database transactions, concurrent customers, payment, cancellation, or malformed
external input. Those boundaries require their own requirements and tests.

BDD is the discovery and feedback practice; Gherkin is a language for recording examples;
pytest-bdd connects those examples to pytest. You can practice BDD without feature files. Use them
when people responsible for the requirements actually review the scenarios.

The overlap between ordinary tests and BDD cases is deliberate here so readers can compare the two
representations. In an application, choose valuable examples at each boundary instead of translating
every existing unit test into Gherkin.

## Check that a scenario can catch a regression

As a temporary learning exercise, change the overselling guard in `inventory.py` from
`quantity > self.available` to `quantity >= self.available`. Then run:

```bash
uv run pytest tests/test_reservations.py -v
```

The exact-availability outline row and the later-customer scenario fail because reserving the last
seats should succeed. Restore `>` and rerun `uv run pytest -v`. This exercise demonstrates the value of
a boundary example without leaving a broken implementation in the project.

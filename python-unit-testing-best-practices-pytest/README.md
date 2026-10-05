[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# Python unit testing best practices

> **Companion article:**
> [Python Unit Testing Best Practices: 10 pytest Rules That Scale](https://istranin.dev/blog/python-unit-testing-best-practices-pytest/)
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## Overview

Run the article's late-fee and overdue-reminder examples as one small project:

- describe tests with Given-When-Then;
- parametrize fee boundaries and reject invalid input;
- request fresh account data through an explicit fixture;
- autospec the email gateway and check the reminder outcome.

The suite adds settled and credit-balance cases to protect the reminder's
no-email path. It does not test the fixture's constant data in isolation.

## Requirements

- Python 3.13 or newer.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for the locked dependencies.

## Run the example

From this directory:

```bash
uv sync --locked
uv run python -m pytest -q
uv run python -m pytest --cov=fees --cov=reminders --cov-branch --cov-report=term-missing
```

Expected: **9 passed**. The coverage report makes uncovered behavior visible;
there is no percentage gate in this example. The abstract gateway's
`NotImplementedError` is not exercised by the mocked email boundary.

## Project files

```text
python-unit-testing-best-practices-pytest/
  fees.py
  reminders.py
  tests/
    conftest.py
    test_fees.py
    test_reminders.py
  pyproject.toml
  uv.lock
```

`Account`, `EmailGateway`, and `send_overdue_reminder` live in
`reminders.py`. The article introduces those pieces in separate sections;
the companion supplies the imports needed to run them together. The shared
`overdue_account` fixture lives in `tests/conftest.py`.

---

[All examples](../README.md#article-examples) · [istranin.dev](https://istranin.dev/) · [Apache-2.0 license](../LICENSE)

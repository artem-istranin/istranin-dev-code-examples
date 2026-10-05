[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# Your first pytest test

> **Companion article:**
> [Pytest for Beginners: Write and Run Your First Python Test](https://istranin.dev/blog/pytest-for-beginners-first-python-test/)
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## Overview

Test a two-file shipping example with plain assertions and Given-When-Then.
Orders of 50 or more get free shipping; smaller orders cost 5. Three tests
cover an ordinary free-shipping order and both sides of the threshold.

## Requirements

- Python 3.13 or newer.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for the locked dependencies.

## Run the example

From this directory:

```bash
uv sync --locked
uv run python -m pytest test_shop.py -v
```

Expected: **3 passed**. The article shows manual environment setup; uv creates
an isolated environment here. The Python example itself remains two files.

## Project files

```text
pytest-for-beginners-first-python-test/
  shop.py
  test_shop.py
  pyproject.toml
  uv.lock
```

## Read a failure

Change the first test's expected cost from 0 to 5, then run that test:

```bash
uv run python -m pytest test_shop.py::test_shipping_is_free_for_large_orders -v
```

It should fail with `assert 0 == 5`. Restore the expected cost to 0 afterward.
Changing the implementation's `>= 50` to `> 50` instead should fail the
threshold test. The examples record two different mistakes: an incorrect
expectation and an incorrect implementation.

---

[All examples](../README.md#article-examples) · [istranin.dev](https://istranin.dev/) · [Apache-2.0 license](../LICENSE)

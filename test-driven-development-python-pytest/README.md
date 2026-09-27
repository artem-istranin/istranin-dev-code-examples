[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# Test-driven development in Python with pytest

> **Companion article:**
> [Test-Driven Development in Python with pytest: A Practical Guide](https://istranin.dev/blog/test-driven-development-python-pytest/)
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## Overview

It demonstrates how a small red-green-refactor cycle can drive an inventory rule:

- reserving seats reduces the available quantity;
- a reservation cannot exceed the available quantity;
- zero and negative reservation quantities are rejected;
- rejected reservations leave inventory unchanged.

## Requirements

- Python 3.13 or newer.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for the locked dependencies.

## Run the example

From the `test-driven-development-python-pytest/` directory, install the locked dependencies and run:

```bash
uv sync --locked
uv run pytest test_inventory.py -v
```

The suite reports four passing cases because the parametrized boundary test runs once for zero and once
for a negative quantity.

Run one behavior by its pytest node ID while working through a TDD cycle:

```bash
uv run pytest test_inventory.py::test_reserving_seats_reduces_available_quantity -q
```

Start with the test, watch it fail for the expected reason, make the smallest production change that
passes, and refactor only while the full suite remains green.

## Project files

```text
test-driven-development-python-pytest/
├── inventory.py
├── test_inventory.py
├── pyproject.toml
└── uv.lock
```

---

[All examples](../README.md#article-examples) · [istranin.dev](https://istranin.dev/) · [Apache-2.0 license](../LICENSE)

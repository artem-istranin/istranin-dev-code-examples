# Test-driven development in Python with pytest

This is the runnable companion project for the istranin.dev article
[Test-Driven Development in Python with pytest: A Practical Guide](https://istranin.dev/blog/test-driven-development-python-pytest/).

It demonstrates how a small red-green-refactor cycle can drive an inventory rule:

- reserving seats reduces the available quantity;
- a reservation cannot exceed the available quantity;
- zero and negative reservation quantities are rejected;
- rejected reservations leave inventory unchanged.

## Project files

```text
test-driven-development-python-pytest/
├── inventory.py
├── test_inventory.py
├── pyproject.toml
└── uv.lock
```

## Run the tests

Install the exact locked dependencies and execute the complete test suite:

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

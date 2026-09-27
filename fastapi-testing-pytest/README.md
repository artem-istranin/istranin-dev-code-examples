[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# FastAPI testing with pytest

> **Companion article:**
> [FastAPI Testing with Pytest: A Practical API Testing Tutorial](https://istranin.dev/blog/fastapi-testing-pytest/)
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## Overview

It demonstrates how to test a FastAPI endpoint through `TestClient`, including:

- a successful JSON request and response;
- the boundary where shipping becomes free;
- missing and invalid request data.

## Requirements

- Python 3.13 or newer.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for the locked dependencies.

## Run the example

From the `fastapi-testing-pytest/` directory, install the locked dependencies and run:

```bash
uv sync --locked
uv run pytest test_main.py -v
```

The suite runs five cases. FastAPI's `TestClient` drives the application in-process, so you do not need
to start Uvicorn or open a network connection.

## Project files

```text
fastapi-testing-pytest/
├── main.py
├── test_main.py
├── pyproject.toml
└── uv.lock
```

---

[All examples](../README.md#article-examples) · [istranin.dev](https://istranin.dev/) · [Apache-2.0 license](../LICENSE)

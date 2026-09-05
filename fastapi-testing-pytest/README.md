# FastAPI testing with pytest

This is the runnable companion project for the istranin.dev article
[FastAPI Testing with Pytest: A Practical API Testing Tutorial](https://istranin.dev/blog/fastapi-testing-pytest/).

It demonstrates how to test a FastAPI endpoint through `TestClient`, including:

- a successful JSON request and response;
- the boundary where shipping becomes free;
- missing and invalid request data.

## Project files

```text
fastapi-testing-pytest/
├── main.py
├── test_main.py
├── pyproject.toml
└── uv.lock
```

## Run the tests

Install the exact locked dependencies and execute the test suite:

```bash
uv sync --locked
uv run pytest test_main.py -v
```

The suite runs five cases. FastAPI's `TestClient` drives the application in-process, so you do not need
to start Uvicorn or open a network connection.

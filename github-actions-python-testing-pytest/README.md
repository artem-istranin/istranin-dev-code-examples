[![istranin.dev](../.github/assets/wordmark.svg)](https://istranin.dev/)

# GitHub Actions Python testing with pytest

> **Companion article:**
> [GitHub Actions Python Testing: A Complete pytest CI Guide](https://istranin.dev/blog/github-actions-python-testing-pytest/)
> by Artem Istranin on [istranin.dev](https://istranin.dev/).

## Overview

Run the article's shipping tests and inspect its complete GitHub Actions
workflow: Python 3.12-3.14, branch coverage, JUnit/XML reports, and one stable
`tests` check.

## Requirements

- Python 3.12 or newer.
- [uv](https://docs.astral.sh/uv/getting-started/installation/) for the locked dependencies.
- A GitHub repository to run the standalone workflow.

## Run the example

From this directory:

```bash
uv sync --locked
uv run python -m pytest -q
uv run python -m pytest --cov=shop --cov-branch --cov-report=term-missing --cov-report=xml:coverage.xml --cov-fail-under=100 --junitxml=test-results/pytest.xml
```

Expected: **5 passed** and **100% statement and branch coverage** for
`shop.py`. Reports are generated locally and excluded from Git.

## Project files

```text
github-actions-python-testing-pytest/
  .github/workflows/tests.yml
  tests/test_shop.py
  shop.py
  pyproject.toml
  requirements-dev.txt
  uv.lock
```

## Use the workflow in a standalone repository

Copy this directory's contents, including `.github/`, to the root of a new
repository with a `main` branch. The nested `.github/workflows/tests.yml`
is the complete workflow from the article. GitHub only discovers workflows
at the repository root, so it does not execute this nested template here.

The template uses `requirements-dev.txt` as shown in the article. This
examples repository uses `pyproject.toml` and `uv.lock` for reproducible
local runs. Their pytest and pytest-cov version ranges match; when adapting
the example, choose the dependency source already used by your project.

The root [example workflow](../.github/workflows/test-examples.yml) tests this
directory with uv on the same three Python versions, checks branch coverage,
and uploads reports. Its paths include the example directory because this
repository contains multiple projects.

Require the standalone workflow's stable `tests` job in branch protection
after confirming that it fails for a broken expectation and passes again
when the correct expectation is restored.

---

[All examples](../README.md#article-examples) · [istranin.dev](https://istranin.dev/) · [Apache-2.0 license](../LICENSE)

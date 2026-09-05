---
name: create-istranin-code-example
description: Create or update a self-contained code project for an istranin.dev article in this repository. Use when adding an article example, synchronizing example code with an article, updating the example index, or extending example CI. Do not use for editing the article itself.
---

# Create an istranin.dev Code Example

Build code readers can clone and run independently while keeping it consistent with the related article.

## Preserve the Repository Model

- Work on a dedicated, feature-focused branch. Commit code, documentation, and CI as separate reviewable changes when each can stand alone.
- Do not push unless the user explicitly asks to publish the branch or create a pull request.
- Use the article slug as the example directory name.
- Treat every example directory as an independent `uv` project. It must have its own `pyproject.toml`, `uv.lock`, and supported Python version.
- Initialize projects with `--no-workspace`; examples must not depend on a repository-level Python environment.
- A small article may use a non-installable application layout such as `main.py` and `test_main.py`. Use an installable `src/` package only when the article itself teaches or requires that layout.
- Keep generated environments and caches out of Git.

## Match the Article

Read the complete related article or draft before writing code. Preserve its filenames, imports, endpoints, payloads, commands, and expected results unless the user explicitly requests a corrected or expanded variant.

Verify version-sensitive library behavior against current official documentation before choosing dependencies. If current behavior conflicts with the article, use the supported behavior in the example and report the exact article correction needed. Do not hide unexpected dependency warnings with a broad warning filter.

The example README must include:

- the article title linked to `https://istranin.dev/blog/<article-slug>/`; linking to a draft URL is allowed;
- the behavior demonstrated by the example;
- a compact file tree;
- exact `uv sync --locked` and `uv run ...` commands;
- the expected successful result or test count.

Do not add placeholder URLs. Use the real article slug supplied by the user or returned by the istranin.dev article tools.

## Update Repository Navigation and CI

Add or update one row in the root `README.md` table of contents. Link to the example directory and summarize its main concepts without duplicating the example README.

Update `.github/workflows/test-examples.yml` so the new example installs its locked dependencies and runs its documented verification command. Preserve pinned action revisions and read-only default permissions. Keep examples isolated: one failing project must identify its own directory clearly in the job or matrix entry.

## Verify and Commit

From the example directory, run:

```bash
uv lock --check
uv sync --locked
uv run <the command documented in the example README>
```

Run any additional checks introduced by the example. Confirm the test count and expected behavior, inspect the complete diff, and ensure the working tree contains no `.venv`, cache, secret, or generated output.

Create independently reviewable Conventional Commits, normally:

1. the runnable project, source, tests, and lockfile;
2. the example README and root table-of-contents entry;
3. CI coverage for the example.

Report the branch, commits, verification result, any upstream warnings, and whether anything was pushed.

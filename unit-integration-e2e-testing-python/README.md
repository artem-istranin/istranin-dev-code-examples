# Unit testing vs integration testing vs E2E in Python

One small command-line unit converter, tested at three boundaries. Adapted from the
testing-levels example in the pytest course, with a smaller conversion model so the
test boundaries stay easy to see.

## Run it

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first. From this
directory:

```bash
uv sync --locked
uv run units-convert 25 C F
uv run pytest -v
```

The command prints `77`. The complete suite has 18 cases. The project uses Python
3.13, pytest, and Typer; `uv.lock` records the tested dependency versions.

The supported symbols are `m`, `cm`, `kg`, `g`, `C`, and `F`. Symbols are
case-sensitive. A successful conversion writes one number to stdout. Unknown units
and incompatible dimensions write an explanation to stderr and exit with code 1.
This teaching example handles ordinary finite numeric inputs; it is not a complete
scientific-units library.

## Where each test starts

| Directory | Real code exercised | Deliberately outside its scope |
| --- | --- | --- |
| `tests/unit/` | Conversion rules with explicit in-memory unit definitions | Packaged JSON and CLI |
| `tests/integration/` | Packaged JSON, resource loader, unit objects, converter | Command parsing and process output |
| `tests/e2e/` | Installed command in a child process, from an unrelated directory | Deployment to a different operating system or a release artifact |

```bash
uv run pytest tests/unit -v
uv run pytest tests/integration -v
uv run pytest tests/e2e -v
```

The E2E tests launch the real `units-convert` executable installed by `uv sync`.
They use pytest's temporary directory as the working directory so an accidental
relative read of `src/unit_converter/units.json` cannot pass. They do not use
Typer's in-process `CliRunner`.

## How conversion works

Each dimension has a base unit: meters, kilograms, or Celsius. `Unit` describes
values with `unit_value = base_value * scale + offset`. Fahrenheit therefore uses
scale `1.8` and offset `32`; centimeters use scale `100` and offset `0`.

`convert` first reverses the source transformation, then applies the target
transformation. `registry.py` reads the bundled JSON definitions. `cli.py` connects
argument parsing, registry loading, conversion, and terminal output.

## Level and purpose are independent

Folders show scope. Markers show why particular tests exist:

```bash
uv run pytest -m acceptance -v
uv run pytest -m regression -v
```

The two acceptance cases check the agreed requirements that temperature conversion
works through the terminal and that incompatible dimensions are rejected. They live
at different levels. The regression marker selects three reverse-temperature cases
that protect against the deliberate defect below; it does not imply a historical
production incident.

## Try a deliberate defect

In `src/unit_converter/converter.py`, temporarily change:

```python
base_value = (value - source.offset) / source.scale
```

to:

```python
base_value = value / source.scale
```

Run `uv run pytest -m regression -v`. All three selected cases should fail because
Fahrenheit's offset must be removed before dividing by its scale. Restore the line
and run `uv run pytest -v` again. The forward `25 C -> 77 F` example alone cannot
catch this defect because the source Celsius offset is zero.

Other useful experiments, one at a time:

| Deliberate change | Unit tests | Integration tests | E2E tests |
| --- | --- | --- | --- |
| Remove `+ target.offset` from the return expression | Fail | Fail | Fail |
| Change only Fahrenheit's JSON offset from `32` to `0` | Pass | Fail | Fail |
| Send the successful result to stderr with `typer.echo(..., err=True)` | Pass | Pass | Fail |

Restore each change before trying another. The point is the distinct failure each
boundary can expose, not a recommended ratio of test counts.

## Optional release-artifact check

An editable development install does not prove that a release wheel contains the
JSON file. To check the built package separately:

```bash
uv build
uv run --isolated --no-project --with ./dist/testing_levels_unit_converter-0.1.0-py3-none-any.whl units-convert 25 C F
```

This should also print `77`. The project uses package resources rather than paths
relative to the repository, and the wheel includes `units.json`.

"""Expose conversions through the installed units-convert command."""

import typer

from unit_converter.converter import convert
from unit_converter.registry import load_units

app = typer.Typer(add_completion=False, pretty_exceptions_enable=False)


@app.command()
def main(value: float, source: str, target: str) -> None:
    """Print a converted value, or report an invalid conversion to stderr."""
    units = load_units()
    for symbol in (source, target):
        if symbol not in units:
            typer.echo(f"Unknown unit: {symbol}", err=True)
            raise typer.Exit(code=1)

    try:
        result = convert(value, units[source], units[target])
    except ValueError as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error

    typer.echo(f"{result:g}")

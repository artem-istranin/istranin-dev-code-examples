"""Load the unit definitions shipped with the application."""

import json
from importlib.resources import files

from unit_converter.converter import Unit


def load_units() -> dict[str, Unit]:
    """Read packaged JSON without relying on the current working directory."""
    text = files("unit_converter").joinpath("units.json").read_text(encoding="utf-8")
    definitions = json.loads(text)
    return {symbol: Unit(**definition) for symbol, definition in definitions.items()}

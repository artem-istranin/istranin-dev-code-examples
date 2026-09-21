"""Convert values without depending on files or a command-line framework."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Unit:
    """Describe a unit as unit_value = base_value * scale + offset."""

    dimension: str
    scale: float = 1.0
    offset: float = 0.0

    def __post_init__(self) -> None:
        if self.scale <= 0:
            raise ValueError("Unit scale must be positive")


def convert(value: float, source: Unit, target: Unit) -> float:
    """Convert compatible units through their shared base unit."""
    if source.dimension != target.dimension:
        raise ValueError("Cannot convert between different dimensions")

    base_value = (value - source.offset) / source.scale
    return base_value * target.scale + target.offset

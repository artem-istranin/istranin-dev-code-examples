import pytest

from unit_converter.converter import convert
from unit_converter.registry import load_units


def test_packaged_temperature_conversion():
    units = load_units()

    result = convert(25, units["C"], units["F"])

    assert result == pytest.approx(77)


@pytest.mark.parametrize(
    "value, source, target, expected",
    [(250, "cm", "m", 2.5), (1.5, "kg", "g", 1500), (750, "g", "kg", 0.75)],
)
def test_packaged_length_and_mass_conversions(value, source, target, expected):
    units = load_units()

    assert convert(value, units[source], units[target]) == pytest.approx(expected)

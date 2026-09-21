import pytest

from unit_converter.converter import Unit, convert


def test_celsius_to_fahrenheit():
    celsius = Unit(dimension="temperature")
    fahrenheit = Unit(dimension="temperature", scale=1.8, offset=32)

    result = convert(25, celsius, fahrenheit)

    assert result == pytest.approx(77)


@pytest.mark.regression
@pytest.mark.parametrize("value, expected", [(32, 0), (77, 25), (-40, -40)])
def test_fahrenheit_to_celsius(value, expected):
    fahrenheit = Unit(dimension="temperature", scale=1.8, offset=32)
    celsius = Unit(dimension="temperature")

    assert convert(value, fahrenheit, celsius) == pytest.approx(expected)


@pytest.mark.parametrize("value, expected", [(0, 0), (1.5, 150), (-2, -200)])
def test_meters_to_centimeters(value, expected):
    meter = Unit(dimension="length")
    centimeter = Unit(dimension="length", scale=100)

    assert convert(value, meter, centimeter) == pytest.approx(expected)


@pytest.mark.acceptance
def test_rejects_incompatible_dimensions():
    meter = Unit(dimension="length")
    kilogram = Unit(dimension="mass")

    with pytest.raises(ValueError, match="different dimensions"):
        convert(1, meter, kilogram)


@pytest.mark.parametrize("scale", [0, -1])
def test_rejects_nonpositive_scale(scale):
    with pytest.raises(ValueError, match="scale must be positive"):
        Unit(dimension="length", scale=scale)

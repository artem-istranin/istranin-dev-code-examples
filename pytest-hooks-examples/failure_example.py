import pytest


def inventory_count() -> int:
    """Return the deliberately incorrect inventory count for this demo."""
    return 2


@pytest.mark.env('staging')
def test_inventory_count() -> None:
    """Fail a staging check so the environment-aware rerun command is visible."""
    assert inventory_count() == 3

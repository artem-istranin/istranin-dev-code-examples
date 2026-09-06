def inventory_count() -> int:
    """Return the deliberately incorrect inventory count for this demo."""
    return 2


def test_inventory_count() -> None:
    """Fail deliberately so the custom terminal summary is visible."""
    assert inventory_count() == 3

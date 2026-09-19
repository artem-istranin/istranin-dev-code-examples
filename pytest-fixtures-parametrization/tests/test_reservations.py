import pytest


@pytest.mark.parametrize(
    ('quantity', 'expected'),
    [
        pytest.param(1, 4, id='reserve-one'),
        pytest.param(4, 1, id='leave-one'),
        pytest.param(5, 0, id='exhaust-stock'),
    ],
)
def test_reserve(stocked_inventory, quantity, expected):
    stocked_inventory.reserve('book', quantity)
    assert stocked_inventory.remaining('book') == expected


@pytest.mark.parametrize('quantity', [6, 10], ids=['one-too-many', 'double-stock'])
def test_overdraw_preserves_stock(stocked_inventory, quantity):
    with pytest.raises(ValueError, match='stock unavailable'):
        stocked_inventory.reserve('book', quantity)
    assert stocked_inventory.remaining('book') == 5


@pytest.mark.parametrize('quantity', [0, -1], ids=['zero', 'negative'])
def test_invalid_quantity_preserves_stock(stocked_inventory, quantity):
    with pytest.raises(ValueError, match='quantity must be positive'):
        stocked_inventory.reserve('book', quantity)
    assert stocked_inventory.remaining('book') == 5

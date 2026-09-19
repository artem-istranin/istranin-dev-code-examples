import pytest


@pytest.mark.parametrize(
    ('prepared_inventory', 'quantity', 'expected'),
    [(5, 2, 3), (10, 4, 6)],
    indirect=['prepared_inventory'],
    ids=['small-order', 'larger-order'],
)
def test_reserve_from_prepared_stock(prepared_inventory, quantity, expected):
    prepared_inventory.reserve('book', quantity)
    assert prepared_inventory.remaining('book') == expected

import pytest

from inventory import Inventory, OutOfStockError


def test_reserving_seats_reduces_available_quantity():
    inventory = Inventory(available=3)

    inventory.reserve(2)

    assert inventory.available == 1


def test_reserving_more_than_available_is_rejected():
    inventory = Inventory(available=2)

    with pytest.raises(OutOfStockError, match='not enough seats'):
        inventory.reserve(3)

    assert inventory.available == 2


@pytest.mark.parametrize('quantity', [0, -1], ids=['zero', 'negative'])
def test_non_positive_quantity_is_rejected(quantity: int):
    inventory = Inventory(available=3)

    with pytest.raises(ValueError, match='quantity must be positive'):
        inventory.reserve(quantity)

    assert inventory.available == 3

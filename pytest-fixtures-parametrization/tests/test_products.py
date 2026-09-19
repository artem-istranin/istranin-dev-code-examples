import pytest


def test_reserving_one_product_leaves_another_unchanged(inventory, make_product):
    book = make_product(sku='book', available=5)
    pen = make_product(sku='pen', available=20)

    inventory.reserve(book, 2)

    assert inventory.remaining(book) == 3
    assert inventory.remaining(pen) == 20


@pytest.mark.parametrize('available', [0, 8], ids=['empty', 'in-stock'])
def test_product_starts_with_requested_balance(inventory, make_product, available):
    sku = make_product(sku='book', available=available)
    assert inventory.remaining(sku) == available


def test_negative_opening_balance_does_not_create_product(inventory):
    with pytest.raises(ValueError, match='available must not be negative'):
        inventory.add('book', -1)
    with pytest.raises(KeyError):
        inventory.remaining('book')


def test_unknown_product_cannot_be_reserved(inventory):
    with pytest.raises(ValueError, match='stock unavailable'):
        inventory.reserve('missing', 1)

def test_reserve_all_available(inventory, opening_stock):
    inventory.add('book', opening_stock)
    inventory.reserve('book', opening_stock)
    assert inventory.remaining('book') == 0

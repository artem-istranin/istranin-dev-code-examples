from shop import shipping_cost


def test_shipping_is_free_for_large_orders():
    order_total = 75

    cost = shipping_cost(order_total)

    assert cost == 0


def test_shipping_costs_five_below_free_shipping_threshold():
    assert shipping_cost(49) == 5


def test_shipping_is_free_at_threshold():
    assert shipping_cost(50) == 0

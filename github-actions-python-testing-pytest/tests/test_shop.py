import pytest

from shop import shipping_cost


@pytest.mark.parametrize(
    ("order_total", "expected_cost"),
    [
        pytest.param(0, 5, id="zero"),
        pytest.param(49, 5, id="below-threshold"),
        pytest.param(50, 0, id="at-threshold"),
        pytest.param(75, 0, id="above-threshold"),
    ],
)
def test_shipping_cost(order_total: int, expected_cost: int) -> None:
    assert shipping_cost(order_total) == expected_cost


def test_shipping_cost_rejects_negative_total() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        shipping_cost(-1)

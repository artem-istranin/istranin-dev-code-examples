import pytest
from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_shipping_quote_returns_free_shipping():
    response = client.post(
        "/shipping-quotes",
        json={"order_total": 75},
    )

    assert response.status_code == 200
    assert response.json() == {"shipping_cost": 0}


@pytest.mark.parametrize(
    ("order_total", "expected_cost"),
    [
        pytest.param(49, 5, id="below-threshold"),
        pytest.param(50, 0, id="at-threshold"),
    ],
)
def test_shipping_quote_handles_free_shipping_boundary(
    order_total: int,
    expected_cost: int,
):
    response = client.post(
        "/shipping-quotes",
        json={"order_total": order_total},
    )

    assert response.status_code == 200
    assert response.json() == {"shipping_cost": expected_cost}


@pytest.mark.parametrize(
    "payload",
    [
        pytest.param({"order_total": -1}, id="negative-total"),
        pytest.param({}, id="missing-total"),
    ],
)
def test_shipping_quote_rejects_invalid_order_total(payload: dict[str, int]):
    response = client.post("/shipping-quotes", json=payload)

    assert response.status_code == 422

    errors = response.json()["detail"]
    assert any(error["loc"][-1] == "order_total" for error in errors)

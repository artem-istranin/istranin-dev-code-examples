def shipping_cost(order_total: int) -> int:
    if order_total < 0:
        raise ValueError("order total must not be negative")
    return 0 if order_total >= 50 else 5

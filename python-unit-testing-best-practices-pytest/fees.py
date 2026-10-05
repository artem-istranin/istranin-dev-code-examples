def late_fee(days_overdue: int) -> int:
    if days_overdue < 0:
        raise ValueError("days overdue must not be negative")
    return min(days_overdue * 2, 20)

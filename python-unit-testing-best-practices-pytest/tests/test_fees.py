import pytest

from fees import late_fee


@pytest.mark.parametrize(
    ("days_overdue", "expected_fee"),
    [
        pytest.param(0, 0, id="due-today"),
        pytest.param(1, 2, id="one-day-overdue"),
        pytest.param(10, 20, id="at-cap"),
        pytest.param(11, 20, id="above-cap"),
    ],
)
def test_late_fee(days_overdue: int, expected_fee: int) -> None:
    assert late_fee(days_overdue) == expected_fee


def test_late_fee_rejects_negative_days() -> None:
    with pytest.raises(ValueError, match="must not be negative"):
        late_fee(-1)


def test_late_fee_is_capped_after_ten_days() -> None:
    days_overdue = 14  # Given

    fee = late_fee(days_overdue)  # When

    assert fee == 20  # Then

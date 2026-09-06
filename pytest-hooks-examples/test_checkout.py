import pytest

from checkout import checkout_message


def test_checkout_is_available_locally() -> None:
    assert checkout_message('local') == 'checkout ready in local'


@pytest.mark.env('staging')
def test_checkout_is_available_in_staging() -> None:
    assert checkout_message('staging') == 'checkout ready in staging'

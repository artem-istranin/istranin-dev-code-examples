import pytest

from reminders import Account


@pytest.fixture
def overdue_account() -> Account:
    return Account(email="reader@example.com", balance_cents=2500)

from unittest.mock import create_autospec

import pytest

from reminders import Account, EmailGateway, send_overdue_reminder


def test_sends_reminder_for_overdue_account(
    overdue_account: Account,
) -> None:
    gateway = create_autospec(EmailGateway, instance=True)

    sent = send_overdue_reminder(overdue_account, gateway)

    assert sent is True
    gateway.send.assert_called_once_with(
        recipient="reader@example.com",
        subject="Payment overdue",
    )


@pytest.mark.parametrize("balance_cents", [0, -100], ids=["settled", "credit"])
def test_does_not_send_reminder_without_outstanding_balance(
    balance_cents: int,
) -> None:
    account = Account(email="reader@example.com", balance_cents=balance_cents)
    gateway = create_autospec(EmailGateway, instance=True)

    sent = send_overdue_reminder(account, gateway)

    assert sent is False
    gateway.send.assert_not_called()

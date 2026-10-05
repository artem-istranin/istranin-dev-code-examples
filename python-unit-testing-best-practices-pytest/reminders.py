from dataclasses import dataclass


@dataclass
class Account:
    email: str
    balance_cents: int


class EmailGateway:
    def send(self, recipient: str, subject: str) -> None:
        raise NotImplementedError


def send_overdue_reminder(
    account: Account,
    gateway: EmailGateway,
) -> bool:
    if account.balance_cents <= 0:
        return False

    gateway.send(
        recipient=account.email,
        subject="Payment overdue",
    )
    return True

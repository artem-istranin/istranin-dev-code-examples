"""An application operation that adds income and reports completion."""

from decimal import Decimal

from wallet.decorators import report
from wallet.main import Wallet


@report
def add_income(wallet: Wallet, amount: Decimal, currency: str) -> Decimal:
    wallet.add(amount, currency)
    return wallet.balance()

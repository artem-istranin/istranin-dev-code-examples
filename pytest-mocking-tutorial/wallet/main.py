"""Maintain an in-memory balance in euros."""

from decimal import Decimal
from pathlib import Path

from wallet.fx import RateProvider


class Wallet:
    def __init__(self, rates_path: Path):
        self.rates = RateProvider(rates_path)
        self._balance = Decimal("0")

    def add(self, amount: Decimal, currency: str) -> None:
        """Add an amount in an uppercase currency code; failed lookups add nothing."""
        rate = (
            Decimal("1")
            if currency == "EUR"
            else self.rates.get_rate(currency, base="EUR")
        )
        self._balance += amount * rate

    def balance(self) -> Decimal:
        """Return the balance in euros, without applying a rounding policy."""
        return self._balance

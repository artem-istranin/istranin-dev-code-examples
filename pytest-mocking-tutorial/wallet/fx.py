"""Read illustrative exchange rates from a local JSON file."""

import json
from decimal import Decimal, InvalidOperation
from pathlib import Path


class RateUnavailable(Exception):
    """The requested currency pair has no usable rate."""


class RateProvider:
    def __init__(self, path: Path):
        self.path = path

    def get_rate(self, currency: str, *, base: str) -> Decimal:
        """Return a positive rate for multiplying currency amounts into base."""
        try:
            rates = json.loads(self.path.read_text(encoding="utf-8"))
            rate = Decimal(rates[f"{currency}/{base}"])
            if not rate.is_finite() or rate <= 0:
                raise ValueError("Rate must be positive and finite")
        except (OSError, ValueError, KeyError, TypeError, InvalidOperation) as error:
            raise RateUnavailable(f"No usable rate for {currency}/{base}") from error
        return rate

class OutOfStockError(Exception):
    """Report that a reservation exceeds the remaining inventory."""


class Inventory:
    """Track available seats and protect reservation boundaries."""

    def __init__(self, available: int) -> None:
        """Create inventory with the supplied number of available seats."""
        self.available = available

    def reserve(self, quantity: int) -> None:
        """Reserve a positive quantity without allowing overselling."""
        self._validate_reservation(quantity)
        self.available -= quantity

    def _validate_reservation(self, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError('quantity must be positive')
        if quantity > self.available:
            raise OutOfStockError('not enough seats')

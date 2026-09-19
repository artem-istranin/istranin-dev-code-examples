import sqlite3


class Inventory:
    """Reserve stock through a caller-owned SQLite connection."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        connection.execute('CREATE TABLE stock (sku TEXT PRIMARY KEY, available INTEGER NOT NULL)')

    def add(self, sku: str, available: int) -> None:
        """Create a product with a nonnegative opening balance."""
        if available < 0:
            raise ValueError('available must not be negative')
        self.connection.execute('INSERT INTO stock VALUES (?, ?)', (sku, available))

    def remaining(self, sku: str) -> int:
        """Read a product's balance, raising KeyError for an unknown product."""
        row = self.connection.execute('SELECT available FROM stock WHERE sku = ?', (sku,)).fetchone()
        if row is None:
            raise KeyError(sku)
        return row[0]

    def reserve(self, sku: str, quantity: int) -> None:
        """Subtract positive stock without permitting an overdraw."""
        if quantity <= 0:
            raise ValueError('quantity must be positive')
        updated = self.connection.execute(
            'UPDATE stock SET available = available - ? WHERE sku = ? AND available >= ?',
            (quantity, sku, quantity),
        )
        if updated.rowcount != 1:
            raise ValueError('stock unavailable')

import sqlite3
from contextlib import closing

from inventory import Inventory


def test_reserve_one():
    with closing(sqlite3.connect(':memory:', autocommit=True)) as conn:
        inventory = Inventory(conn)
        inventory.add('book', 5)
        inventory.reserve('book', 1)
        assert inventory.remaining('book') == 4


def test_leave_one():
    with closing(sqlite3.connect(':memory:', autocommit=True)) as conn:
        inventory = Inventory(conn)
        inventory.add('book', 5)
        inventory.reserve('book', 4)
        assert inventory.remaining('book') == 1


def test_exhaust_stock():
    with closing(sqlite3.connect(':memory:', autocommit=True)) as conn:
        inventory = Inventory(conn)
        inventory.add('book', 5)
        inventory.reserve('book', 5)
        assert inventory.remaining('book') == 0

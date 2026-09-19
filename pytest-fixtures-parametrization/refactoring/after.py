import sqlite3
from contextlib import closing

import pytest

from inventory import Inventory


@pytest.fixture
def stocked_inventory():
    with closing(sqlite3.connect(':memory:', autocommit=True)) as conn:
        inventory = Inventory(conn)
        inventory.add('book', 5)
        yield inventory


@pytest.mark.parametrize(
    ('quantity', 'expected'),
    [
        pytest.param(1, 4, id='reserve-one'),
        pytest.param(4, 1, id='leave-one'),
        pytest.param(5, 0, id='exhaust-stock'),
    ],
)
def test_reserve(stocked_inventory, quantity, expected):
    stocked_inventory.reserve('book', quantity)
    assert stocked_inventory.remaining('book') == expected

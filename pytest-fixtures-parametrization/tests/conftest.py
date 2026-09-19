import sqlite3
from contextlib import closing

import pytest

from inventory import Inventory


def pytest_addoption(parser):
    parser.addoption(
        '--opening-stock',
        action='append',
        type=int,
        default=[],
        help='Opening stock for dynamic cases; repeat for multiple cases',
    )


def pytest_generate_tests(metafunc):
    if 'opening_stock' in metafunc.fixturenames:
        values = metafunc.config.getoption('opening_stock') or [1, 5]
        if any(value < 1 for value in values):
            raise pytest.UsageError('--opening-stock must be positive')
        values = sorted(set(values))
        metafunc.parametrize('opening_stock', values, ids=[f'stock-{value}' for value in values])


@pytest.fixture(params=['memory', 'file'])
def connection(request, tmp_path):
    path = ':memory:' if request.param == 'memory' else tmp_path / 'stock.sqlite3'
    with closing(sqlite3.connect(path, autocommit=True)) as conn:
        yield conn


@pytest.fixture
def inventory(connection):
    return Inventory(connection)


@pytest.fixture
def stocked_inventory(inventory):
    inventory.add('book', 5)
    return inventory


@pytest.fixture
def make_product(inventory):
    def create(*, sku, available=5):
        inventory.add(sku, available)
        return sku

    return create


@pytest.fixture
def prepared_inventory(request, inventory):
    inventory.add('book', request.param)
    return inventory

from time import perf_counter, sleep

import pytest

SETUP_TIMES = pytest.StashKey[list[float]]()


def pytest_addoption(parser):
    parser.addoption('--catalog-scope', choices=['function', 'session'], default='function')


def catalog_scope(*, fixture_name, config):
    return config.getoption('catalog_scope')


@pytest.fixture(scope=catalog_scope)
def catalog(request):
    started = perf_counter()
    sleep(0.1)  # Controlled setup cost, not a production benchmark.
    result = tuple(range(10))
    elapsed = perf_counter() - started
    request.config.stash.setdefault(SETUP_TIMES, []).append(elapsed)
    return result


def pytest_terminal_summary(terminalreporter, config):
    times = config.stash.get(SETUP_TIMES, [])
    terminalreporter.write_line(f'catalog setups={len(times)}; measured setup={sum(times):.3f}s')

from __future__ import annotations

from collections.abc import Generator

import pytest


FAILED_TESTS = pytest.StashKey[list[str]]()


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add the environment selector used by this test suite."""
    parser.addoption(
        '--env',
        action='store',
        default='local',
        choices=('local', 'staging'),
        help='run tests for the selected environment',
    )


def pytest_configure(config: pytest.Config) -> None:
    """Register the environment marker in pytest's active configuration."""
    config.addinivalue_line(
        'markers',
        'env(name): run the test only for the named environment',
    )


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: list[pytest.Item],
) -> None:
    """Skip tests whose environment marker does not match ``--env``."""
    selected_env = config.getoption('--env')

    for item in items:
        env_marker = item.get_closest_marker('env')
        if env_marker is None:
            continue

        required_env = env_marker.args[0]
        if required_env != selected_env:
            item.add_marker(pytest.mark.skip(reason=f'requires --env={required_env}'))


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(
    item: pytest.Item,
    call: pytest.CallInfo[None],
) -> Generator[None, pytest.TestReport, pytest.TestReport]:
    """Remember failed test calls after other report hooks have run."""
    report = yield

    if report.when == 'call' and report.failed:
        failed_test_ids = item.config.stash.setdefault(FAILED_TESTS, [])
        failed_test_ids.append(report.nodeid)

    return report


def pytest_terminal_summary(
    terminalreporter: pytest.TerminalReporter,
    config: pytest.Config,
) -> None:
    """Add a compact failure list to the end of terminal output."""
    failed_test_ids = config.stash.get(FAILED_TESTS, [])
    if not failed_test_ids:
        return

    terminalreporter.section('failed tests for triage')
    for nodeid in failed_test_ids:
        terminalreporter.write_line(nodeid)

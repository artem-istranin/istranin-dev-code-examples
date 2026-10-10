import shlex

import pytest


ENVIRONMENTS = ('local', 'staging')
FAILED_TESTS = pytest.StashKey[set[str]]()


def pytest_addoption(parser):
    """Add the environment selector used by this test suite."""
    parser.addoption(
        '--env',
        action='store',
        default='local',
        choices=ENVIRONMENTS,
        help='run tests for the selected environment',
    )


def pytest_configure(config):
    """Register the environment marker in pytest's active configuration."""
    config.addinivalue_line(
        'markers',
        "env(name): run only in the named environment ('local' or 'staging')",
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests whose environment marker does not match ``--env``."""
    selected_env = config.getoption('--env')

    for item in items:
        env_marker = item.get_closest_marker('env')
        if env_marker is None:
            continue

        if (
            len(env_marker.args) != 1
            or env_marker.kwargs
            or env_marker.args[0] not in ENVIRONMENTS
        ):
            raise pytest.UsageError(
                f'{item.nodeid}: env marker requires exactly one positional '
                "argument: 'local' or 'staging'"
            )

        required_env = env_marker.args[0]
        if required_env != selected_env:
            item.add_marker(pytest.mark.skip(reason=f'requires --env={required_env}'))


@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item):
    """Remember tests with failures in setup, the test body, or cleanup."""
    report = yield

    if report.failed:
        item.config.stash.setdefault(FAILED_TESTS, set()).add(report.nodeid)

    return report


def pytest_terminal_summary(terminalreporter, config):
    """Print a command to rerun failed tests in the selected environment."""
    failed_test_ids = sorted(config.stash.get(FAILED_TESTS, set()))
    if not failed_test_ids:
        return

    environment = config.getoption('--env')
    command = shlex.join(
        ['uv', 'run', 'pytest', f'--env={environment}', '-q', *failed_test_ids]
    )
    terminalreporter.section(f'CHECKOUT CHECK: {environment.upper()}')
    terminalreporter.write_line(f'Tests needing attention: {len(failed_test_ids)}')
    terminalreporter.write_line('Rerun just these tests:')
    terminalreporter.write_line(command)

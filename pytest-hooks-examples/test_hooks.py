import shlex
from pathlib import Path

import pytest


pytest_plugins = ('pytester',)


@pytest.mark.parametrize(
    'arguments',
    [
        '',
        "'local', 'staging'",
        "name='staging'",
        "'staging', note='extra'",
        "'production'",
        '42',
    ],
    ids=['missing', 'extra', 'keyword', 'mixed', 'unknown', 'non-string'],
)
def test_invalid_environment_marker_reports_usage_error(
    pytester: pytest.Pytester, arguments: str
) -> None:
    plugin_source = Path(__file__).with_name('conftest.py').read_text(encoding='utf-8')
    pytester.makeconftest(plugin_source)
    pytester.makepyfile(
        test_bad_marker=f"""
        import pytest

        @pytest.mark.env({arguments})
        def test_bad_marker():
            pass
        """
    )

    result = pytester.runpytest('-q')

    assert result.ret == pytest.ExitCode.USAGE_ERROR
    result.assert_outcomes()
    result.stderr.fnmatch_lines(
        ["*test_bad_marker.py::test_bad_marker*env marker*'local'*'staging'*"]
    )


@pytest.mark.parametrize('environment', ['local', 'staging'])
def test_environment_selection_preserves_unmarked_tests(
    pytester: pytest.Pytester, environment: str
) -> None:
    plugin_source = Path(__file__).with_name('conftest.py').read_text(encoding='utf-8')
    pytester.makeconftest(plugin_source)
    pytester.makepyfile(
        test_environments="""
        import pytest

        def test_unmarked():
            pass

        @pytest.mark.env('local')
        def test_local():
            pass

        @pytest.mark.env('staging')
        def test_staging():
            pass
        """
    )

    result = pytester.runpytest('-v', f'--env={environment}')

    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=2, skipped=1)
    assert 'test_unmarked PASSED' in result.stdout.str()
    assert f'test_{environment} PASSED' in result.stdout.str()


@pytest.mark.parametrize('environment', ['local', 'staging'])
def test_rerun_command_selects_only_failures_in_the_same_environment(
    pytester: pytest.Pytester, environment: str
) -> None:
    plugin_source = Path(__file__).with_name('conftest.py').read_text(encoding='utf-8')
    pytester.makeconftest(plugin_source)
    pytester.makepyfile(
        test_failure="""
        import pytest

        @pytest.mark.parametrize('cart', [1, 2], ids=['cart total [EUR]', 'empty'])
        def test_failure(cart):
            assert False

        def test_success():
            pass

        @pytest.mark.xfail(reason='known bug')
        def test_expected_failure():
            assert False

        @pytest.mark.skip(reason='not ready')
        def test_skipped():
            assert False
        """
    )

    result = pytester.runpytest('-q', f'--env={environment}')

    result.assert_outcomes(failed=2, passed=1, skipped=1, xfailed=1)
    result.stdout.fnmatch_lines(
        [
            f'*CHECKOUT CHECK: {environment.upper()}*',
            '*Tests needing attention: 2',
            '*Rerun just these tests:',
        ]
    )
    command = next(line for line in result.stdout.lines if line.startswith('uv run '))
    arguments = shlex.split(command)
    assert arguments == [
        'uv',
        'run',
        'pytest',
        f'--env={environment}',
        '-q',
        'test_failure.py::test_failure[cart total [EUR]]',
        'test_failure.py::test_failure[empty]',
    ]

    rerun = pytester.runpytest(*arguments[3:])

    assert rerun.ret == pytest.ExitCode.TESTS_FAILED
    rerun.assert_outcomes(failed=2)


def test_rerun_command_includes_setup_and_cleanup_failures_once(
    pytester: pytest.Pytester,
) -> None:
    plugin_source = Path(__file__).with_name('conftest.py').read_text(encoding='utf-8')
    pytester.makeconftest(plugin_source)
    pytester.makepyfile(
        test_errors="""
        import pytest

        @pytest.fixture
        def broken_setup():
            assert False

        @pytest.fixture
        def broken_cleanup():
            yield
            assert False

        def test_setup(broken_setup):
            pass

        def test_cleanup(broken_cleanup):
            pass

        def test_call_and_cleanup(broken_cleanup):
            assert False
        """
    )

    result = pytester.runpytest('-q')

    assert result.ret == pytest.ExitCode.TESTS_FAILED
    result.assert_outcomes(failed=1, passed=1, errors=3)
    result.stdout.fnmatch_lines(
        [
            '*Tests needing attention: 3',
            'uv run pytest --env=local -q '
            'test_errors.py::test_call_and_cleanup '
            'test_errors.py::test_cleanup test_errors.py::test_setup',
        ]
    )


def test_successful_run_has_no_rerun_command(pytester: pytest.Pytester) -> None:
    plugin_source = Path(__file__).with_name('conftest.py').read_text(encoding='utf-8')
    pytester.makeconftest(plugin_source)
    pytester.makepyfile('def test_success(): pass')

    result = pytester.runpytest('-q')

    assert result.ret == pytest.ExitCode.OK
    result.assert_outcomes(passed=1)
    assert 'CHECKOUT CHECK:' not in result.stdout.str()
    assert 'uv run pytest' not in result.stdout.str()

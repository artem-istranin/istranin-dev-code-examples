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


def test_failed_tests_are_listed_for_triage(pytester: pytest.Pytester) -> None:
    plugin_source = Path(__file__).with_name('conftest.py').read_text(encoding='utf-8')
    pytester.makeconftest(plugin_source)
    pytester.makepyfile(
        test_failure="""
        def test_failure():
            assert False
        """
    )

    result = pytester.runpytest('-q')

    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(
        [
            '*failed tests for triage*',
            'test_failure.py::test_failure',
        ]
    )

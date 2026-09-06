from pathlib import Path

import pytest


pytest_plugins = ('pytester',)


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

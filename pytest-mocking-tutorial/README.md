# Pytest mocking tutorial

A small wallet demonstrates `pytest-mock` without requiring an API key, network
access, or a database. A $100 deposit at the illustrative USD/EUR rate of 0.90
adds €90. A failed rate lookup must leave the existing balance unchanged.

The provider reads a local JSON file. The wallet tests replace that dependency;
the integration tests keep it real. The example intentionally omits persistence,
historical rates, currency validation, and money-rounding rules.

## Run the example

Use Python 3.13+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).
From this directory:

```bash
uv sync --locked
uv run pytest -q
```

The lockfile pins pytest 9.1.1 and pytest-mock 3.15.1. All 16 tests should pass.
There are no live network calls in the application or test suite.

## Follow the progression

1. Read `wallet/main.py`. `Wallet.add()` updates a euro balance using a separate
   `RateProvider`. A lookup failure happens before the balance changes.
2. Run `uv run pytest tests/test_wallet.py -v`. The first test uses
   `mocker.patch.object` to replace a method. The next tests replace the provider
   class, configure its instance through `return_value`, and raise an exception
   with `side_effect`.
3. Compare the class patch with and without `autospec=True, spec_set=True`.
   Autospeccing checks available methods and call signatures. `spec_set` also
   rejects assigning unknown attributes. Neither validates a configured return
   value or proves the real provider works.
4. Follow `from wallet.fx import RateProvider` in `wallet/main.py`. Replacing
   the whole class requires the target `wallet.main.RateProvider`, because that
   is the name the wallet looks up. Replacing only the original module's name
   after the import leaves the wallet's reference unchanged.
5. Read `wallet/decorators.py` and `wallet/reported.py`, then run
   `uv run pytest tests/test_reporting.py tests/test_import_time_patch.py -v`.
   Most tests leave the decorator active and patch the event destination.
   One tests the body via `__wrapped__`. Another replaces the decorator before
   the first import in a fresh Python process.
6. Run `uv run pytest tests/test_real_rates.py -v`. These tests read actual
   temporary JSON files and exercise the real wallet/provider connection.

## Why isolate the decorator-import example?

Python applies `@report` when it defines the function, normally during import.
Patching `report` later does not remove an installed wrapper. Importing inside a
fixture is not sufficient if another test has already imported that module.

`test_import_time_patch.py` starts the current environment's Python interpreter
with `sys.executable`. It patches the decorator with `unittest.mock.patch` before
importing the decorated function. The subprocess has no pytest fixture system,
so it uses the standard-library context manager behind `mocker.patch`.
The child process discards its import state when it exits. The test is safe to
run before or after `test_reporting.py`; it does not reload or mutate shared
modules in the pytest process.

The ordinary reporting tests exercise the real decorator's success and failure
behavior. Bypassing a wrapper does not test that wrapper, and should not be the
only coverage for authorization, transactions, retries, or similar guarantees.

## Sources

- [pytest-mock usage](https://pytest-mock.readthedocs.io/en/latest/usage.html)
- [Python: where to patch](https://docs.python.org/3/library/unittest.mock.html#where-to-patch)
- [Python: autospeccing](https://docs.python.org/3/library/unittest.mock.html#autospeccing)

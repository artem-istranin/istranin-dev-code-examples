"""Use a fresh interpreter so other tests cannot pre-import the decorated module."""

import subprocess
import sys
from pathlib import Path


def test_patch_decorator_before_first_import():
    script = """
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

with patch("wallet.decorators.report", new=lambda func: func):
    from wallet.reported import add_income

from wallet.main import Wallet

wallet = Wallet(Path("unused.json"))
assert add_income(wallet, Decimal("20"), "EUR") == Decimal("20")
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=10,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == ""  # The reporting wrapper was never installed.

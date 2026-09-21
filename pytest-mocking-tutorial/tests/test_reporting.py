from decimal import Decimal

import pytest

from wallet.fx import RateUnavailable
from wallet.main import Wallet
from wallet.reported import add_income


def test_reports_success_without_replacing_the_decorator(mocker, tmp_path):
    report_event = mocker.patch("wallet.decorators.report_event", autospec=True)
    wallet = Wallet(tmp_path / "unused.json")

    assert add_income(wallet, Decimal("20"), "EUR") == Decimal("20")
    report_event.assert_called_once_with("add_income completed")


def test_failed_income_is_not_reported_as_completed(mocker, tmp_path):
    report_event = mocker.patch("wallet.decorators.report_event", autospec=True)
    wallet = Wallet(tmp_path / "missing.json")

    with pytest.raises(RateUnavailable):
        add_income(wallet, Decimal("100"), "USD")

    assert wallet.balance() == Decimal("0")
    report_event.assert_not_called()


def test_can_test_the_body_without_reporting(mocker, tmp_path):
    report_event = mocker.patch("wallet.decorators.report_event", autospec=True)
    wallet = Wallet(tmp_path / "unused.json")

    result = add_income.__wrapped__(wallet, Decimal("20"), "EUR")

    assert result == Decimal("20")
    report_event.assert_not_called()

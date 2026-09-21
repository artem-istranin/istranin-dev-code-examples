from decimal import Decimal

import pytest

from wallet.fx import RateProvider, RateUnavailable
from wallet.main import Wallet


def test_add_dollars_with_patched_method(mocker, tmp_path):
    get_rate = mocker.patch.object(
        RateProvider, "get_rate", return_value=Decimal("0.90")
    )
    wallet = Wallet(tmp_path / "unused.json")

    wallet.add(Decimal("100"), "USD")

    assert wallet.balance() == Decimal("90")
    get_rate.assert_called_once_with("USD", base="EUR")


def test_add_dollars_with_patched_class(mocker, tmp_path):
    provider_class = mocker.patch(
        "wallet.main.RateProvider", autospec=True, spec_set=True
    )
    provider = provider_class.return_value
    provider.get_rate.return_value = Decimal("0.90")
    wallet = Wallet(tmp_path / "unused.json")

    wallet.add(Decimal("100"), "USD")

    assert wallet.balance() == Decimal("90")
    provider.get_rate.assert_called_once_with("USD", base="EUR")


def test_missing_rate_leaves_existing_balance_unchanged(mocker, tmp_path):
    provider_class = mocker.patch(
        "wallet.main.RateProvider", autospec=True, spec_set=True
    )
    provider_class.return_value.get_rate.side_effect = RateUnavailable("Offline")
    wallet = Wallet(tmp_path / "unused.json")
    wallet.add(Decimal("20"), "EUR")

    with pytest.raises(RateUnavailable, match="Offline"):
        wallet.add(Decimal("100"), "USD")

    assert wallet.balance() == Decimal("20")


def test_euros_do_not_need_a_rate(mocker, tmp_path):
    get_rate = mocker.patch.object(RateProvider, "get_rate")
    wallet = Wallet(tmp_path / "missing.json")

    wallet.add(Decimal("20"), "EUR")
    wallet.add(Decimal("-5"), "EUR")

    assert wallet.balance() == Decimal("15")
    get_rate.assert_not_called()

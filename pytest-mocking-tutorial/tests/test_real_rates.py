from decimal import Decimal

import pytest

from wallet.fx import RateProvider, RateUnavailable
from wallet.main import Wallet


def test_wallet_reads_real_rates(tmp_path):
    rates_path = tmp_path / "rates.json"
    rates_path.write_text('{"USD/EUR": "0.90"}', encoding="utf-8")
    wallet = Wallet(rates_path)

    wallet.add(Decimal("100"), "USD")
    wallet.add(Decimal("20"), "EUR")

    assert wallet.balance() == Decimal("110")


@pytest.mark.parametrize(
    "contents",
    [
        "{}",
        "not json",
        '{"USD/EUR": "zero"}',
        '{"USD/EUR": "0"}',
        '{"USD/EUR": "NaN"}',
        '{"USD/EUR": "-1"}',
    ],
)
def test_unusable_rate_does_not_change_balance(tmp_path, contents):
    path = tmp_path / "rates.json"
    path.write_text(contents, encoding="utf-8")
    wallet = Wallet(path)
    wallet.add(Decimal("20"), "EUR")

    with pytest.raises(RateUnavailable, match="USD/EUR"):
        wallet.add(Decimal("100"), "USD")

    assert wallet.balance() == Decimal("20")


def test_missing_rate_file(tmp_path):
    provider = RateProvider(tmp_path / "missing.json")

    with pytest.raises(RateUnavailable, match="USD/EUR"):
        provider.get_rate("USD", base="EUR")

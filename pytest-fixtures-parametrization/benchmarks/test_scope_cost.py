import pytest


@pytest.mark.parametrize('product', range(10))
def test_catalog_contains_product(catalog, product):
    assert product in catalog

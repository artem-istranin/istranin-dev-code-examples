"""Apply credential isolation to every offline test."""

import pytest


@pytest.fixture(autouse=True)
def no_provider_credentials(monkeypatch):
    """Remove ambient provider secrets; adapter fixtures supply dummy keys."""
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        monkeypatch.delenv(name, raising=False)

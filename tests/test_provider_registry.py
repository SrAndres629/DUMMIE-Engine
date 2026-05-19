from __future__ import annotations

from dummie.providers import DummieProviderRegistry


def test_registry_loading() -> None:
    reg = DummieProviderRegistry()
    status = reg.get_providers_status(live_check=True)
    assert "gemini_cli" in status
    assert "deepseek" in status


def test_registry_never_exposes_secret_values() -> None:
    reg = DummieProviderRegistry()
    status = reg.get_providers_status(live_check=True)
    serialized = str(status)
    assert "sk-" not in serialized
    assert "API_KEY" not in serialized

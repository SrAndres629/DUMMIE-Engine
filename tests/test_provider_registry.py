from dummie.providers import DummieProviderRegistry

def test_registry_loading():
    reg = DummieProviderRegistry()
    status = reg.get_providers_status()
    assert "gemini_cli" in status
    assert status["gemini_cli"]["configured"] is True

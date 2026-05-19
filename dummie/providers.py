import yaml
import json
from pathlib import Path
from dummie.paths import AIWG

class DummieProviderRegistry:
    def __init__(self):
        self.registry_path = AIWG / "providers" / "provider_registry.yaml"
        self.status_path = AIWG / "providers" / "provider_status.json"

    def get_providers_status(self) -> dict:
        # Load registry
        registry = {}
        if self.registry_path.exists():
            try:
                with open(self.registry_path, "r", encoding="utf-8") as f:
                    registry = yaml.safe_load(f) or {}
            except Exception:
                pass
        
        # Load status
        status = {}
        if self.status_path.exists():
            try:
                with open(self.status_path, "r", encoding="utf-8") as f:
                    status = json.load(f) or {}
            except Exception:
                pass

        results = {}
        providers_list = registry.get("providers", {})
        statuses_list = status.get("providers", {})

        for name, info in providers_list.items():
            st = statuses_list.get(name, {})
            results[name] = {
                "type": info.get("type", "unknown"),
                "configured": st.get("configured", False),
                "cli_available": st.get("cli_available", False),
                "auth_status": st.get("auth_status", "unknown"),
                "secret_storage": info.get("secret_storage", "external")
            }
        return results

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from dummie.paths import AIWG


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass
class ProviderStatus:
    provider_id: str
    provider_type: str
    configured: bool
    cli_available: bool
    auth_status: str
    secret_storage: str
    capabilities: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.provider_type,
            "configured": self.configured,
            "cli_available": self.cli_available,
            "auth_status": self.auth_status,
            "secret_storage": self.secret_storage,
            "capabilities": self.capabilities,
        }


class DummieProviderRegistry:
    API_ENV_MAP = {
        "openrouter": "OPENROUTER_API_KEY",
        "groq": "GROQ_API_KEY",
        "deepseek": "DEEPSEEK_API_KEY",
    }

    CLI_MAP = {
        "gemini_cli": ["gemini", "gemini-cli"],
        "codex_cli": ["codex"],
        "opencode": ["opencode"],
    }

    CAPABILITY_MAP = {
        "gemini_cli": ["text", "code"],
        "codex_cli": ["code", "repo_ops"],
        "antigravity": ["ide_agent"],
        "openrouter": ["api_text", "api_code"],
        "groq": ["api_text", "api_reasoning"],
        "deepseek": ["api_text", "api_code"],
        "opencode": ["local_cli", "model_routing"],
    }

    def __init__(self):
        self.providers_dir = AIWG / "providers"
        self.providers_dir.mkdir(parents=True, exist_ok=True)

        self.registry_path = self.providers_dir / "provider_registry.yaml"
        self.status_path = self.providers_dir / "provider_status.json"
        self.auth_policy_path = self.providers_dir / "provider_auth_policy.yaml"

    def get_providers_status(self, live_check: bool = False) -> dict[str, dict[str, Any]]:
        registry = self._load_registry()
        provider_map = registry.get("providers", {})
        cached_status = self._load_cached_status()

        result: dict[str, dict[str, Any]] = {}
        for provider_id, info in provider_map.items():
            if live_check:
                status = self._resolve_live_status(provider_id, info)
            else:
                status = cached_status.get(provider_id)
                if not status:
                    status = self._resolve_live_status(provider_id, info)

            result[provider_id] = status

        if live_check:
            self._write_status(result)

        return result

    def check_providers(self) -> dict[str, Any]:
        status = self.get_providers_status(live_check=True)
        return {
            "decision": "PASS",
            "generated_at": _utc_now(),
            "providers": status,
            "secret_policy": "no_secrets_in_repo",
        }

    def _resolve_live_status(self, provider_id: str, info: dict[str, Any]) -> dict[str, Any]:
        provider_type = str(info.get("type", "unknown"))
        secret_storage = str(info.get("secret_storage", "external"))

        cli_available = self._cli_available(provider_id)
        configured = self._provider_configured(provider_id, provider_type)

        if provider_type in {"api", "api_or_web"}:
            auth_status = "ready" if configured else "requires_auth"
        elif provider_type in {"local_cli", "ide_agent"}:
            if cli_available and configured:
                auth_status = "ready"
            elif cli_available:
                auth_status = "requires_login"
            else:
                auth_status = "unknown"
        else:
            auth_status = "unknown"

        model = ProviderStatus(
            provider_id=provider_id,
            provider_type=provider_type,
            configured=configured,
            cli_available=cli_available,
            auth_status=auth_status,
            secret_storage=secret_storage,
            capabilities=self.CAPABILITY_MAP.get(provider_id, []),
        )
        return model.to_dict()

    def _provider_configured(self, provider_id: str, provider_type: str) -> bool:
        if provider_type in {"api", "api_or_web"}:
            env_name = self.API_ENV_MAP.get(provider_id)
            return bool(env_name and os.environ.get(env_name))

        if provider_id == "opencode":
            return self._opencode_has_credentials()

        if provider_id in {"gemini_cli", "codex_cli", "antigravity"}:
            return self._cli_available(provider_id)

        return False

    def _cli_available(self, provider_id: str) -> bool:
        if provider_id == "opencode":
            local_opencode = AIWG / "tools" / "opencode" / "node_modules" / ".bin" / "opencode"
            if local_opencode.exists():
                return True
        bins = self.CLI_MAP.get(provider_id, [])
        for binary in bins:
            path = shutil.which(binary)
            if path:
                return True
        return False

    def _opencode_has_credentials(self) -> bool:
        base = AIWG / "tools" / "opencode-data" / "opencode" / "auth.json"
        if not base.exists():
            return False
        try:
            data = json.loads(base.read_text(encoding="utf-8"))
        except Exception:
            return False
        creds = data.get("credentials", []) if isinstance(data, dict) else []
        return bool(creds)

    def _load_registry(self) -> dict[str, Any]:
        if not self.registry_path.exists():
            return {"providers": {}}
        try:
            return yaml.safe_load(self.registry_path.read_text(encoding="utf-8")) or {"providers": {}}
        except Exception:
            return {"providers": {}}

    def _load_cached_status(self) -> dict[str, dict[str, Any]]:
        if not self.status_path.exists():
            return {}
        try:
            payload = json.loads(self.status_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
        return payload.get("providers", {}) if isinstance(payload, dict) else {}

    def _write_status(self, providers_status: dict[str, dict[str, Any]]) -> None:
        payload = {
            "last_check": _utc_now(),
            "providers": providers_status,
        }
        self.status_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")

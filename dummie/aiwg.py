from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from dummie.paths import AIWG, DEFAULT_EXCLUDED_PATHS


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


class DummieAiwgIntegration:
    def __init__(self):
        self.aiwg_root = AIWG
        self.state_dir = AIWG / "state"
        self.reports_dir = AIWG / "reports"
        self.receipts_dir = AIWG / "receipts"
        self.identity_dir = AIWG / "identity"

        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        self.receipts_dir.mkdir(parents=True, exist_ok=True)
        self.identity_dir.mkdir(parents=True, exist_ok=True)

    def load_json(self, path: Path, default: dict | list | None = None) -> Any:
        if not path.exists():
            return {} if default is None else default
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {} if default is None else default

    def load_yaml(self, path: Path, default: dict | list | None = None) -> Any:
        if not path.exists():
            return {} if default is None else default
        try:
            return yaml.safe_load(path.read_text(encoding="utf-8")) or ({} if default is None else default)
        except Exception:
            return {} if default is None else default

    def run_preflight(self) -> dict[str, Any]:
        truth = self.load_json(self.state_dir / "current_truth.json", default={})
        active_pack = self.load_json(self.state_dir / "active_pack.json", default={})
        organism_manifest = self.load_json(self.state_dir / "organism_manifest.json", default={})
        read_policy = self.load_json(self.state_dir / "agent_read_policy.json", default={})

        current_pack = active_pack.get("active_pack") or truth.get("current_pack") or "PACK_S1"

        return {
            "status": "PASS",
            "timestamp": _utc_now(),
            "active_pack": current_pack,
            "degraded_capabilities": truth.get("degraded_capabilities", []),
            "organism_manifest_loaded": bool(organism_manifest),
            "read_policy_loaded": bool(read_policy),
            "excluded_paths": read_policy.get("excluded_paths", DEFAULT_EXCLUDED_PATHS),
        }

    def load_identity_bundle(self) -> dict[str, Any]:
        return {
            "creator_profile": self.load_yaml(self.identity_dir / "creator_profile.yaml", default={}),
            "dummie_identity": self.load_yaml(self.identity_dir / "dummie_identity.yaml", default={}),
            "strategic_partner_contract": self.load_yaml(self.identity_dir / "strategic_partner_contract.yaml", default={}),
        }

    def write_receipt(self, command: str, status: str, details: dict[str, Any]) -> dict[str, Any]:
        receipt = {
            "receipt_id": f"rcpt_{uuid.uuid4().hex[:12]}",
            "command": command,
            "status": status,
            "timestamp": _utc_now(),
            "details": details,
        }
        path = self.receipts_dir / f"{receipt['receipt_id']}.json"
        path.write_text(json.dumps(receipt, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        return receipt

    def write_report(self, filename: str, content: dict[str, Any]) -> Path:
        path = self.reports_dir / filename
        path.write_text(json.dumps(content, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        return path

    def write_markdown_report(self, filename: str, content: str) -> Path:
        path = self.reports_dir / filename
        path.write_text(content.rstrip() + "\n", encoding="utf-8")
        return path

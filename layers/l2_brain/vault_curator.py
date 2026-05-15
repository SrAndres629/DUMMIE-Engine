from __future__ import annotations

import json
import logging
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger(__name__)

_FORBIDDEN_PATTERNS = [
    (re.compile(r"\.env\s*[=:]", re.I), "forbidden .env assignment"),
    (re.compile(r"secret\s*(is|[:=])", re.I), "forbidden secret value"),
    (re.compile(r"credential\s*(is|[:=])", re.I), "forbidden credential value"),
    (re.compile(r"token\s*[=:]", re.I), "forbidden token assignment"),
    (re.compile(r"password\s*[=:]", re.I), "forbidden password assignment"),
    (re.compile(r"chain_of_thought", re.I), "private reasoning"),
    (re.compile(r"private reasoning", re.I), "private reasoning"),
    (re.compile(r"private_reasoning", re.I), "private reasoning"),
]


class VaultCurator:
    def __init__(self, root: str | Path = ".aiwg/vault"):
        self.root = Path(root)

    def extract_vault_entries(self, mission_id: str, workbench_path: str | Path) -> list[dict]:
        path = Path(workbench_path)
        if not path.exists():
            return []

        entries = []

        # 1. Look for golden paths in final_summary.md (heuristic)
        summary_path = path / "final_summary.md"
        if summary_path.exists():
             content = summary_path.read_text(encoding="utf-8")
             if "golden path" in content.lower() or "success pattern" in content.lower():
                 entries.append({
                     "entry_type": "golden_path",
                     "summary": f"Successful execution pattern for mission {mission_id}",
                     "evidence_refs": [str(summary_path)],
                 })

        # 2. Look for failed patterns in validation_report.md
        report_path = path / "validation_report.md"
        if report_path.exists():
            content = report_path.read_text(encoding="utf-8")
            if "fail" in content.lower() or "error" in content.lower() or "regression" in content.lower():
                entries.append({
                    "entry_type": "failed_pattern",
                    "summary": f"Known pitfalls and regressions in {mission_id}",
                    "evidence_refs": [str(report_path)],
                })

        # 3. Look for decisions in decision_log.jsonl
        log_path = path / "decision_log.jsonl"
        if log_path.exists():
            with log_path.open("r", encoding="utf-8") as h:
                lines = [line.strip() for line in h if line.strip()]
                if lines:
                    entries.append({
                        "entry_type": "decision",
                        "summary": f"Key architectural decisions from {mission_id}",
                        "evidence_refs": [str(log_path)],
                    })

        # Add common metadata
        for entry in entries:
            entry.update({
                "vault_id": f"vlt-{uuid.uuid4().hex[:8]}",
                "mission_id": mission_id,
                "created_at": _now(),
                "reuse_conditions": [],
                "risk_notes": [],
            })

        return entries

    def store_vault_entry(self, entry: dict) -> dict:
        self._reject_private(entry)

        self.root.mkdir(parents=True, exist_ok=True)
        vault_id = entry.get("vault_id") or f"vlt-{uuid.uuid4().hex[:8]}"
        entry["vault_id"] = vault_id
        entry["created_at"] = entry.get("created_at") or _now()

        entry_path = self.root / f"{vault_id}.json"
        self._write_json(entry_path, entry)

        self.build_vault_index()
        return entry

    def list_entries(self, entry_type: str = "") -> list[dict]:
        if not self.root.exists():
            return []

        entries = []
        for item in self.root.glob("vlt-*.json"):
            try:
                data = json.loads(item.read_text(encoding="utf-8"))
                if not entry_type or data.get("entry_type") == entry_type:
                    entries.append(data)
            except Exception as e:
                logger.warning(f"Failed to read vault entry {item}: {e}")
        return entries

    def build_vault_index(self) -> dict:
        entries = self.list_entries()
        index = {
            "updated_at": _now(),
            "total_entries": len(entries),
            "by_type": {},
            "by_mission": {},
        }

        for e in entries:
            etype = e.get("entry_type", "unknown")
            index["by_type"].setdefault(etype, []).append(e["vault_id"])

            mid = e.get("mission_id", "unknown")
            index["by_mission"].setdefault(mid, []).append(e["vault_id"])

        self._write_json(self.root / "vault_index.json", index)
        return index

    def finalize_and_clean(self, mission_id: str, workbench_path: str | Path) -> dict:
        # Step 1: Extract
        entries = self.extract_vault_entries(mission_id, workbench_path)

        # Step 2: Store
        stored = []
        for entry in entries:
            try:
                stored.append(self.store_vault_entry(entry))
            except Exception as e:
                logger.error(f"Failed to store vault entry: {e}")

        # Step 3: Cleanup policy (we retain for now)
        return {
            "mission_id": mission_id,
            "vault_entries_created": len(stored),
            "stored_ids": [s["vault_id"] for s in stored],
            "cleanup_status": "retained",
        }

    def _reject_private(self, value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                self._reject_private(str(key))
                self._reject_private(item)
        elif isinstance(value, (list, tuple, set)):
            for item in value:
                self._reject_private(item)
        elif isinstance(value, str):
            for pattern, reason in _FORBIDDEN_PATTERNS:
                if pattern.search(value):
                    raise ValueError(f"vault payload contains {reason}")

    def _write_json(self, path: Path, payload: dict) -> None:
        self._reject_private(payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.tmp")
        content = json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
        tmp.write_text(content, encoding="utf-8")
        with tmp.open("a", encoding="utf-8") as h:
            h.flush()
            try:
                os.fsync(h.fileno())
            except OSError:
                pass
        tmp.replace(path)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

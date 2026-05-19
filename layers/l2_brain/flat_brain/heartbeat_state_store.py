# Spec: 165_heartbeat_state_store
# Spec: DE-V2-L2-165
"""Heartbeat State Store — HEARTBEAT-0

Append-only JSONL ledger for heartbeat history.  Provides idempotent
writes, latest retrieval, and next-seed management.
"""

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class HeartbeatStateStore:
    def __init__(self, aiwg_root: Path = Path(".aiwg")):
        self.root = aiwg_root / "heartbeat"
        self.root.mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.root / "heartbeat_ledger.jsonl"
        self.latest_path = self.root / "latest_heartbeat.json"
        self.seed_path = self.root / "next_heartbeat_seed.json"
        self.index_path = self.root / "heartbeat_index.json"

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def _load_index(self) -> Dict[str, Any]:
        if self.index_path.exists():
            try:
                return json.loads(self.index_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

    def _save_index(self, index: Dict[str, Any]):
        self.index_path.write_text(json.dumps(index, indent=2), encoding="utf-8")

    # ------------------------------------------------------------------
    # Append
    # ------------------------------------------------------------------

    def append_heartbeat(self, heartbeat: Dict[str, Any]):
        hb_id = heartbeat.get("heartbeat_id", "")
        if not hb_id:
            return

        # Idempotent check
        index = self._load_index()
        if hb_id in index:
            return

        # Append to JSONL
        with self.ledger_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(heartbeat) + "\n")

        # Update latest
        self.latest_path.write_text(json.dumps(heartbeat, indent=2), encoding="utf-8")

        # Update index
        index[hb_id] = {
            "mode": heartbeat.get("mode", ""),
            "decision": heartbeat.get("decision", ""),
            "selected_action": heartbeat.get("selected_action", {}).get("action_type", ""),
            "created_at": heartbeat.get("created_at", ""),
        }
        self._save_index(index)

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    def latest_heartbeat(self) -> Optional[Dict[str, Any]]:
        if self.latest_path.exists():
            try:
                return json.loads(self.latest_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return None

    def iter_heartbeats(self):
        if not self.ledger_path.exists():
            return
        with self.ledger_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    yield json.loads(line)

    # ------------------------------------------------------------------
    # Next seed
    # ------------------------------------------------------------------

    def write_next_seed(self, seed: Dict[str, Any]):
        self.seed_path.write_text(json.dumps(seed, indent=2), encoding="utf-8")

    def load_next_seed(self) -> Dict[str, Any]:
        if self.seed_path.exists():
            try:
                return json.loads(self.seed_path.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {}

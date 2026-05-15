from __future__ import annotations

import json
import os
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:
    fcntl = None

logger = logging.getLogger(__name__)

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

class GraphSyncLedger:
    """
    [L2_BRAIN] Append-only ledger for graph synchronization events.
    """
    def __init__(self, root: str | Path = ".aiwg/graph_sync"):
        self.root = Path(root)
        self.ledger_path = self.root / "graph_sync_ledger.jsonl"
        self.lock_path = self.root / ".ledger.lock"

    def append_event(self, sync_id: str, event_type: str, data: dict | None = None) -> dict:
        self.root.mkdir(parents=True, exist_ok=True)
        
        event = {
            "event_id": f"evt-{os.urandom(4).hex()}",
            "sync_id": sync_id,
            "event_type": event_type,
            "timestamp": _now(),
            "data": data or {}
        }
        
        # We don't do full idempotency check for every event here to keep it fast, 
        # but we use lock to prevent corruption.
        with open(self.lock_path, "a") as lock_file:
            if fcntl:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                with open(self.ledger_path, "a", encoding="utf-8") as h:
                    h.write(json.dumps(event, sort_keys=True) + "\n")
                    h.flush()
                    try:
                        os.fsync(h.fileno())
                    except OSError:
                        pass
            finally:
                if fcntl:
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
        
        # If it's a plan, save it as latest_plan.json
        if event_type == "GRAPH_SYNC_PLAN_CREATED" and data and "plan" in data:
            self._save_latest_plan(data["plan"])
            
        return event

    def _save_latest_plan(self, plan: dict):
        plan_path = self.root / "latest_plan.json"
        tmp_path = plan_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as h:
            json.dump(plan, h, indent=2, sort_keys=True)
            h.flush()
            try:
                os.fsync(h.fileno())
            except OSError:
                pass
        os.replace(tmp_path, plan_path)

    def list_events(self, sync_id: str = "") -> list[dict]:
        if not self.ledger_path.exists():
            return []
        
        events = []
        with open(self.ledger_path, "r", encoding="utf-8") as h:
            for line in h:
                if line.strip():
                    evt = json.loads(line)
                    if not sync_id or evt.get("sync_id") == sync_id:
                        events.append(evt)
        return events

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
        
        with open(self.lock_path, "a") as lock_file:
            if fcntl:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
            try:
                # Idempotency check for PLAN_CREATED
                if event_type == "GRAPH_SYNC_PLAN_CREATED" and self.ledger_path.exists():
                    with open(self.ledger_path, "r", encoding="utf-8") as h:
                        for line in h:
                            if not line.strip(): continue
                            try:
                                existing = json.loads(line)
                                if existing.get("sync_id") == sync_id and existing.get("event_type") == event_type:
                                    return existing
                            except json.JSONDecodeError:
                                continue

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
        tmp_path = plan_path.with_name(f".{plan_path.name}.tmp")
        with open(tmp_path, "w", encoding="utf-8") as h:
            json.dump(plan, h, indent=2, sort_keys=True)
            h.flush()
            try:
                os.fsync(h.fileno())
            except OSError:
                pass
        os.replace(tmp_path, plan_path)

    def get_latest_plan(self) -> dict | None:
        plan_path = self.root / "latest_plan.json"
        if not plan_path.exists():
            return None
        try:
            with open(plan_path, "r", encoding="utf-8") as h:
                return json.load(h)
        except Exception:
            return None

    def list_events(self, sync_id: str = "") -> list[dict]:
        if not self.ledger_path.exists():
            return []
        
        events = []
        with open(self.ledger_path, "r", encoding="utf-8") as h:
            for line_no, line in enumerate(h, 1):
                if not line.strip():
                    continue
                try:
                    evt = json.loads(line)
                    if not sync_id or evt.get("sync_id") == sync_id:
                        events.append(evt)
                except json.JSONDecodeError as e:
                    logger.warning(f"Corrupt ledger line at {self.ledger_path}:{line_no}: {e}")
        return events

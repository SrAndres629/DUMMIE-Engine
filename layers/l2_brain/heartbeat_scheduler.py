"""Heartbeat Scheduler — HEARTBEAT-0

Manual scheduler for heartbeat execution.  No background daemon.
No infinite loop.  No timers.  No autonomous execution.

Usage:
    python3 layers/l2_brain/heartbeat_scheduler.py once
    python3 layers/l2_brain/heartbeat_scheduler.py dry-run
    python3 layers/l2_brain/heartbeat_scheduler.py seed
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict


class HeartbeatScheduler:
    def __init__(self, aiwg_root: Path = Path(".aiwg")):
        self.aiwg_root = aiwg_root
        self.reports = aiwg_root / "reports"
        self.reports.mkdir(parents=True, exist_ok=True)

    def load_next_seed(self) -> Dict[str, Any]:
        from heartbeat_state_store import HeartbeatStateStore
        store = HeartbeatStateStore(aiwg_root=self.aiwg_root)
        return store.load_next_seed()

    def dry_run(self) -> Dict[str, Any]:
        """Simulate a heartbeat without persisting state beyond a dry-run report."""
        seed = self.load_next_seed()
        from heartbeat_decision_policy import select_next_action
        policy = select_next_action(aiwg_root=self.aiwg_root)

        result = {
            "type": "dry_run",
            "decision": "PASS_WITH_WARNINGS",
            "next_seed": seed,
            "would_select": policy.selected_action,
            "would_dispatch": policy.dispatch_recommendation,
            "blocked": policy.blocked_actions,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        (self.reports / "heartbeat_scheduler_latest.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8")
        return result

    def run_once(self, mode: str = "observe_only") -> Dict[str, Any]:
        """Execute exactly one heartbeat cycle."""
        from heartbeat_lifecycle_runtime import run_heartbeat
        result = run_heartbeat(mode=mode, aiwg_root=self.aiwg_root)

        scheduler_report = {
            "type": "run_once",
            "heartbeat_id": result.get("heartbeat_id", ""),
            "decision": result.get("decision", ""),
            "mode": mode,
            "selected_action": result.get("selected_action", {}),
            "dispatch_recommendation": result.get("dispatch_recommendation", ""),
            "next_heartbeat_seed": result.get("next_heartbeat_seed", {}),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        (self.reports / "heartbeat_scheduler_latest.json").write_text(
            json.dumps(scheduler_report, indent=2), encoding="utf-8")
        return scheduler_report


def main():
    args = sys.argv[1:] if len(sys.argv) > 1 else ["once"]
    command = args[0]
    scheduler = HeartbeatScheduler()

    if command == "once":
        mode = args[1] if len(args) > 1 else "observe_only"
        result = scheduler.run_once(mode=mode)
        print(json.dumps(result, indent=2))
    elif command == "dry-run":
        result = scheduler.dry_run()
        print(json.dumps(result, indent=2))
    elif command == "seed":
        seed = scheduler.load_next_seed()
        print(json.dumps(seed, indent=2))
    else:
        print(f"Unknown command: {command}. Use: once, dry-run, seed")
        sys.exit(1)


if __name__ == "__main__":
    main()

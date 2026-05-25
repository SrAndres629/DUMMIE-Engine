#!/usr/bin/env python3
"""Autonomous Heartbeat Scheduler — Continuous observe → dispatch → audit → signal loop.

This IS the conductor (director de orquesta). It:
1. Runs heartbeat diagnostics to observe system state
2. Routes actions through group chat coordinator (@planner/@builder/@reviewer)
3. Manages role-based sessions (plan/build/review reuse)
4. Dispatches to isolated git worktrees for safe execution
5. Audits results with multi-model verification
6. Records everything in .aiwg with full traceability

Usage:
    python3 heartbeat_autonomous.py           # Continuous loop
    python3 heartbeat_autonomous.py once      # One cycle
    python3 heartbeat_autonomous.py status    # Show current orchestrator state

Systemd: dummie-heartbeat.service
"""

import json
import logging
import signal
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from heartbeat_lifecycle_runtime import run_heartbeat
from heartbeat_orchestrator import HeartbeatOrchestrator
from heartbeat_signal import generate_signal, update_heartbeat_md, load_latest_heartbeat
from group_chat_coordinator import GroupChatCoordinator
from heartbeat.heartbeat_event_gate import should_run_heartbeat

_PATH = Path("/opt/dummie-engine")
AIWG_ROOT = _PATH / ".aiwg"
HEARTBEAT_DIR = AIWG_ROOT / "heartbeat"

logger = logging.getLogger("heartbeat-autonomous")

ACTIVE_HEARTBEAT_INTERVAL_S = 60
IDLE_HEARTBEAT_INTERVAL_S = 300
DEGRADED_HEARTBEAT_INTERVAL_S = 600


def resolve_runtime_mode(last_user_event_s: float, cpu: float, queue_depth: int) -> str:
    if cpu >= 0.9 or queue_depth >= 20:
        return "degraded"
    if last_user_event_s <= 120:
        return "active"
    return "idle"


class AutonomousHeartbeatLoop:
    HEARTBEAT_INTERVAL = 300
    ORCHESTRATOR_INTERVAL = 60

    def __init__(self):
        self.running = False
        self.orchestrator = HeartbeatOrchestrator()
        self.coordinator = GroupChatCoordinator(AIWG_ROOT)
        self.last_heartbeat = 0
        self.last_orchestrator = 0
        self.cycles = 0
        self.last_user_event = 9999.0
        self.last_cpu = 0.0
        self.last_queue_depth = 0

    def setup_signals(self):
        import asyncio

        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            try:
                loop.add_signal_handler(
                    sig, lambda s=sig: setattr(self, "running", False)
                )
            except NotImplementedError:
                pass

    def run_forever(self):
        self.running = True
        logger.info(
            "Conductor started (heartbeat=%ds, orchestrator=%ds)",
            self.HEARTBEAT_INTERVAL,
            self.ORCHESTRATOR_INTERVAL,
        )

        while self.running:
            try:
                now = time.time()
                self._tick(now)
            except Exception as e:
                logger.exception("Conductor loop error: %s", e)
            time.sleep(15)

    def _tick(self, now: float):
        activity = []

        if now - self.last_orchestrator >= self.ORCHESTRATOR_INTERVAL:
            self.last_orchestrator = now
            orch_result = self._run_orchestrator()
            if orch_result:
                activity.append(orch_result)

        mode = resolve_runtime_mode(
            self.last_user_event, self.last_cpu, self.last_queue_depth
        )
        interval = {
            "active": ACTIVE_HEARTBEAT_INTERVAL_S,
            "idle": IDLE_HEARTBEAT_INTERVAL_S,
            "degraded": DEGRADED_HEARTBEAT_INTERVAL_S,
        }.get(mode, self.HEARTBEAT_INTERVAL)

        if should_run_heartbeat(
            event_type=None,
            now_ts=now,
            last_hb_ts=self.last_heartbeat,
            interval_s=interval,
        ):
            self.last_heartbeat = now
            hb_result = self._run_heartbeat(mode=mode)
            activity.append(hb_result)

        if activity:
            self._update_signal()
            summary = " | ".join(a.get("type", a.get("status", "?")) for a in activity)
            logger.info("Cycle %d: %s", self.cycles, summary)

    def _run_heartbeat(self, mode: str = "advisory") -> dict:
        try:
            result = run_heartbeat(mode=mode, aiwg_root=AIWG_ROOT)
            self.cycles += 1
            return {
                "type": "heartbeat",
                "status": result.get("decision", "?"),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            logger.error("Heartbeat diagnostic failed: %s", e)
            return {"type": "heartbeat", "status": "error", "error": str(e)}

    def _run_orchestrator(self) -> dict:
        try:
            existing = self.orchestrator.active_task_status()
            if existing and existing.get("status") in ("executing", "auditing"):
                result = self.orchestrator.check_and_audit()
                if result:
                    self._log_conductor_event("audit", result)
                    return {"type": "audit_complete", **result}

            latest_hb = HEARTBEAT_DIR / "latest_heartbeat.json"
            if not latest_hb.exists():
                return {
                    "type": "orchestrator",
                    "status": "skipped",
                    "reason": "No heartbeat data",
                }

            hb = json.loads(latest_hb.read_text())
            selected_action = hb.get("selected_action")
            if not selected_action:
                return {
                    "type": "orchestrator",
                    "status": "skipped",
                    "reason": "No action selected",
                }

            action_type = selected_action.get("action_type", "unknown")
            role = self.coordinator.resolve_role(
                selected_action.get("description", action_type)
            )
            chain = self.coordinator.activate_role_chain(role)

            self._log_conductor_event(
                "dispatch",
                {
                    "action_type": action_type,
                    "role": role,
                    "chain": chain,
                },
            )

            result = self.orchestrator.dispatch(
                selected_action,
                hb.get("decision", "UNKNOWN"),
                hb.get("dispatch_recommendation", "human_review"),
                hb.get("blocked_actions", []),
            )
            result["assigned_role"] = role
            result["pipeline_chain"] = chain
            return {"type": "dispatch", **result}
        except Exception as e:
            logger.error("Orchestrator error: %s", e)
            return {"type": "orchestrator", "status": "error", "error": str(e)}

    def _log_conductor_event(self, event_type: str, data: dict):
        conductor_log = AIWG_ROOT / "heartbeat" / "conductor_log.jsonl"
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "cycle": self.cycles,
            **data,
        }
        with open(conductor_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    def _update_signal(self):
        try:
            hb = load_latest_heartbeat()
            signal_data = generate_signal(hb) if hb else {"status": "initializing"}

            active_task = self.orchestrator.active_task_status()
            if active_task:
                signal_data["active_task"] = active_task

            recent = self.orchestrator.recently_completed(3)
            if recent:
                signal_data["recently_completed"] = [
                    {
                        "task_id": r["task_id"],
                        "status": r["status"],
                        "action": r.get("action_type", "?"),
                    }
                    for r in recent
                ]

            group_state = self.coordinator.load_state()
            signal_data["group_chat"] = {
                "pipeline": group_state.get("pipeline_status", "idle"),
                "active_role": group_state.get("active_role"),
                "chain": group_state.get("pipeline_chain", []),
            }

            signal_file = HEARTBEAT_DIR / "signal.json"
            signal_file.write_text(json.dumps(signal_data, indent=2, default=str))
            update_heartbeat_md(signal_data)
        except Exception as e:
            logger.error("Signal update error: %s", e)


def run_once():
    loop = AutonomousHeartbeatLoop()
    loop.last_heartbeat = 0
    loop.last_orchestrator = 0
    loop.running = True
    loop._tick(time.time())
    print(
        json.dumps(
            {
                "orchestrator_state": loop.orchestrator.state,
                "active_task": loop.orchestrator.active_task_status(),
                "recent": loop.orchestrator.recently_completed(3),
            },
            indent=2,
            default=str,
        )
    )


def run_status():
    orchestrator = HeartbeatOrchestrator()
    print(
        json.dumps(
            {
                "active_task": orchestrator.active_task_status(),
                "recently_completed": orchestrator.recently_completed(5),
            },
            indent=2,
            default=str,
        )
    )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    cmd = sys.argv[1] if len(sys.argv) > 1 else "forever"
    if cmd == "once":
        run_once()
    elif cmd == "status":
        run_status()
    elif cmd == "forever":
        loop = AutonomousHeartbeatLoop()
        loop.run_forever()
    else:
        print(f"Usage: {sys.argv[0]} [forever|once|status]")

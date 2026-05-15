from __future__ import annotations

import json
import logging
import os
import re
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Iterable

try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore

from layers.l2_brain.models import AuthorityLevel

logger = logging.getLogger(__name__)

EVENT_TYPES = {
    "MISSION_CREATED",
    "PHASE_REGISTERED",
    "PHASE_STARTED",
    "PHASE_COMPLETED",
    "PHASE_BLOCKED",
    "PHASE_PAUSED",
    "PHASE_RESUMED",
    "CHECKPOINT_CREATED",
    "RECOVERY_PACKET_CREATED",
    "NEXT_ACTION_SELECTED",
    "MISSION_COMPLETED",
    "MISSION_FAILED",
}
_SAFE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")

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

AUTHORITY_LEVEL_VALUES = {item.value for item in AuthorityLevel}


class PhaseLedger:
    def __init__(self, root: str | Path = ".aiwg/missions"):
        self.root = Path(root)

    def create_mission(self, mission_id: str, user_goal: str, phases: list[dict]) -> dict:
        self._validate_id("mission_id", mission_id)
        self._reject_private({"user_goal": user_goal, "phases": phases})
        self._mission_dir(mission_id).mkdir(parents=True, exist_ok=True)

        self.append_event(
            mission_id,
            {
                "event_type": "MISSION_CREATED",
                "user_goal": user_goal,
            },
        )
        for phase in phases:
            phase_id = str(phase.get("phase_id", ""))
            self._validate_id("phase_id", phase_id)
            authority_level = str(phase.get("authority_level", ""))
            if authority_level and authority_level not in AUTHORITY_LEVEL_VALUES:
                raise ValueError(f"Unsupported authority_level: {authority_level}")
            self.append_event(
                mission_id,
                {
                    "event_type": "PHASE_REGISTERED",
                    "phase_id": phase_id,
                    "authority_level": authority_level,
                    "depends_on": list(phase.get("depends_on", []) or []),
                    "metadata": dict(phase.get("metadata", {}) or {}),
                },
            )

        state = self.current_state(mission_id)
        self._write_json(self._current_state_path(mission_id), state)
        return state

    def append_event(self, mission_id: str, event: dict) -> dict:
        self._validate_id("mission_id", mission_id)
        self._reject_private(event)
        event_type = str(event.get("event_type", ""))
        if event_type not in EVENT_TYPES:
            raise ValueError(f"Unsupported phase ledger event_type: {event_type}")

        phase_id = event.get("phase_id")
        if phase_id:
            self._validate_id("phase_id", str(phase_id))
        for dep in event.get("depends_on", []) or []:
            self._validate_id("phase dependency", str(dep))

        event_id = event.get("event_id")

        ledger_path = self._ledger_path(mission_id)
        self._mission_dir(mission_id).mkdir(parents=True, exist_ok=True)

        with self._lock_ledger(mission_id) as handle:
            # Idempotency check: read existing events while locked
            if event_id:
                handle.seek(0)
                for line in handle:
                    if line.strip():
                        existing = json.loads(line)
                        if existing.get("event_id") == event_id:
                            return existing

            normalized = {
                "event_id": event_id or f"evt-{uuid.uuid4().hex}",
                "event_type": event_type,
                "mission_id": mission_id,
                "timestamp": event.get("timestamp") or _now(),
            }
            normalized.update({key: value for key, value in event.items() if key not in normalized})

            handle.seek(0, os.SEEK_END)
            handle.write(json.dumps(normalized, ensure_ascii=True, sort_keys=True) + "\n")
            handle.flush()
            try:
                os.fsync(handle.fileno())
            except OSError:
                pass  # fsync might not be supported on all filesystems/OS

        return normalized

    def iter_events(self, mission_id: str) -> Iterable[dict]:
        self._validate_id("mission_id", mission_id)
        ledger_path = self._ledger_path(mission_id)
        if not ledger_path.exists():
            return iter(())

        def _reader():
            with self._lock_ledger(mission_id, mode="r") as handle:
                for line in handle:
                    if line.strip():
                        yield json.loads(line)

        return _reader()

    def current_state(self, mission_id: str) -> dict:
        self._validate_id("mission_id", mission_id)
        state: dict[str, Any] = {
            "mission_id": mission_id,
            "user_goal": "",
            "status": "unknown",
            "phases": {},
            "current_phase": "",
            "completed_phases": [],
            "blocked_phases": [],
            "checkpoints": [],
            "key_decisions": [],
            "evidence_refs": [],
            "tests_last_run": {"commands": [], "passed": 0, "failed": 0},
            "known_failures": [],
            "next_action": {},
            "recovery_packet_ref": "",
            "token_ledger_ref": f".aiwg/missions/{mission_id}/token_cost_ledger.jsonl" if mission_id else "",
        }
        for event in self.iter_events(mission_id):
            self._apply_event(state, event)
        return state

    def create_checkpoint(self, mission_id: str, phase_id: str, payload: dict) -> dict:
        self._validate_id("mission_id", mission_id)
        self._validate_id("phase_id", phase_id)
        self._reject_private(payload)

        checkpoint_dir = self._mission_dir(mission_id) / "checkpoints"
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_ref = f".aiwg/missions/{mission_id}/checkpoints/{phase_id}.json"
        checkpoint_path = checkpoint_dir / f"{phase_id}.json"
        checkpoint_payload = {
            "mission_id": mission_id,
            "phase_id": phase_id,
            "created_at": _now(),
            "payload": payload,
        }
        self._write_json(checkpoint_path, checkpoint_payload)
        event = self.append_event(
            mission_id,
            {
                "event_type": "CHECKPOINT_CREATED",
                "phase_id": phase_id,
                "checkpoint_ref": checkpoint_ref,
                "payload": payload,
            },
        )
        self._write_json(self._current_state_path(mission_id), self.current_state(mission_id))
        return event

    def generate_recovery_packet(self, mission_id: str) -> dict:
        self._validate_id("mission_id", mission_id)
        state = self.current_state(mission_id)
        recovery_ref = f".aiwg/missions/{mission_id}/recovery_packet.md"
        recovery_path = self._mission_dir(mission_id) / "recovery_packet.md"
        content = self._recovery_markdown(state)
        self._write_text(recovery_path, content)
        event = self.append_event(
            mission_id,
            {
                "event_type": "RECOVERY_PACKET_CREATED",
                "recovery_packet_ref": recovery_ref,
            },
        )
        self._write_json(self._current_state_path(mission_id), self.current_state(mission_id))
        return {
            "event_type": event["event_type"],
            "mission_id": mission_id,
            "recovery_packet_ref": recovery_ref,
        }

    def select_next_action(self, mission_id: str) -> dict:
        self._validate_id("mission_id", mission_id)
        state = self.current_state(mission_id)
        action = self._derive_next_action(state)
        self._write_json(self._mission_dir(mission_id) / "next_action.json", action)
        self.append_event(
            mission_id,
            {
                "event_type": "NEXT_ACTION_SELECTED",
                "next_action": action,
            },
        )
        self._write_json(self._current_state_path(mission_id), self.current_state(mission_id))
        return action

    def _derive_next_action(self, state: dict) -> dict:
        if state["current_phase"]:
            return {
                "recommended": "continue_phase",
                "phase_id": state["current_phase"],
                "reason": "phase_running",
                "blocked_by": [],
            }
        if state["status"] == "paused":
            return {"recommended": "resume_mission", "reason": "mission_paused", "blocked_by": []}
        if state["blocked_phases"]:
            return {
                "recommended": "inspect_blocked_phase",
                "phase_id": state["blocked_phases"][0],
                "reason": "phase_blocked",
                "blocked_by": state["blocked_phases"],
            }
        completed = set(state["completed_phases"])
        for phase_id, phase in state["phases"].items():
            if phase.get("status") in {"completed", "running"}:
                continue
            pending = [dep for dep in phase.get("depends_on", []) if dep not in completed]
            if not pending:
                return {
                    "recommended": "start_phase",
                    "phase_id": phase_id,
                    "reason": "next_registered_phase_ready",
                    "blocked_by": [],
                }
        if state["phases"]:
            return {"recommended": "complete_mission", "reason": "all_phases_completed", "blocked_by": []}
        return {"recommended": "define_phases", "reason": "no_registered_phases", "blocked_by": []}

    def _apply_event(self, state: dict, event: dict) -> None:
        event_type = event["event_type"]
        phase_id = event.get("phase_id", "")
        if event_type == "MISSION_CREATED":
            state["user_goal"] = event.get("user_goal", "")
            state["status"] = "created"
        elif event_type == "PHASE_REGISTERED":
            state["phases"][phase_id] = {
                "phase_id": phase_id,
                "status": "registered",
                "authority_level": event.get("authority_level", ""),
                "depends_on": list(event.get("depends_on", []) or []),
                "metadata": dict(event.get("metadata", {}) or {}),
            }
        elif event_type == "PHASE_STARTED":
            self._phase(state, phase_id)["status"] = "running"
            state["current_phase"] = phase_id
            state["status"] = "running"
            if phase_id in state["blocked_phases"]:
                state["blocked_phases"].remove(phase_id)
        elif event_type == "PHASE_COMPLETED":
            phase = self._phase(state, phase_id)
            phase["status"] = "completed"
            phase["outcome"] = dict(event.get("outcome", {}) or {})
            if phase_id not in state["completed_phases"]:
                state["completed_phases"].append(phase_id)
            if phase_id in state["blocked_phases"]:
                state["blocked_phases"].remove(phase_id)
            if state["current_phase"] == phase_id:
                state["current_phase"] = ""
        elif event_type == "PHASE_BLOCKED":
            self._phase(state, phase_id)["status"] = "blocked"
            if phase_id not in state["blocked_phases"]:
                state["blocked_phases"].append(phase_id)
            state["known_failures"].append(event.get("reason", "phase_blocked"))
            if state["current_phase"] == phase_id:
                state["current_phase"] = ""
        elif event_type == "PHASE_PAUSED":
            state["status"] = "paused"
        elif event_type == "PHASE_RESUMED":
            state["status"] = "running"
        elif event_type == "CHECKPOINT_CREATED":
            checkpoint = {
                "phase_id": phase_id,
                "checkpoint_ref": event.get("checkpoint_ref", ""),
            }
            state["checkpoints"].append(checkpoint)
            payload = dict(event.get("payload", {}) or {})
            state["evidence_refs"].extend(payload.get("evidence_refs", []) or [])
            if payload.get("tests"):
                state["tests_last_run"] = payload["tests"]
            state["key_decisions"].extend(payload.get("key_decisions", []) or [])
        elif event_type == "RECOVERY_PACKET_CREATED":
            state["recovery_packet_ref"] = event.get("recovery_packet_ref", "")
        elif event_type == "NEXT_ACTION_SELECTED":
            state["next_action"] = dict(event.get("next_action", {}) or {})
        elif event_type == "MISSION_COMPLETED":
            state["status"] = "completed"
        elif event_type == "MISSION_FAILED":
            state["status"] = "failed"
            state["known_failures"].append(event.get("reason", "mission_failed"))

    def _phase(self, state: dict, phase_id: str) -> dict:
        if phase_id not in state["phases"]:
            state["phases"][phase_id] = {"phase_id": phase_id, "status": "unknown", "depends_on": []}
        return state["phases"][phase_id]

    def _recovery_markdown(self, state: dict) -> str:
        next_action = state.get("next_action") or self._derive_next_action(state)
        return "\n".join(
            [
                "# Recovery Packet",
                "",
                "## Mission Goal",
                state.get("user_goal", ""),
                "",
                "## Current Phase",
                state.get("current_phase", "") or "NONE",
                "",
                "## Completed Phases",
                _markdown_list(state.get("completed_phases", [])),
                "",
                "## Blocked Phases",
                _markdown_list(state.get("blocked_phases", [])),
                "",
                "## Key Decisions",
                _markdown_list(state.get("key_decisions", [])),
                "",
                "## Evidence Refs",
                _markdown_list(state.get("evidence_refs", [])),
                "",
                "## Tests Last Run",
                json.dumps(state.get("tests_last_run", {}), ensure_ascii=True, sort_keys=True),
                "",
                "## Known Failures",
                _markdown_list(state.get("known_failures", [])),
                "",
                "## Next Action",
                json.dumps(next_action, ensure_ascii=True, sort_keys=True),
                "",
                "## Do Not Repeat",
                "- Do not persist hidden reasoning.",
                "- Do not write mission files outside `.aiwg/missions`.",
                "",
            ]
        )

    def _mission_dir(self, mission_id: str) -> Path:
        self._validate_id("mission_id", mission_id)
        root = self.root.resolve()
        target = (self.root / mission_id).resolve()
        if os.path.commonpath([str(root), str(target)]) != str(root):
            raise ValueError("mission_id rejected: path traversal is not allowed")
        return target

    def _ledger_path(self, mission_id: str) -> Path:
        return self._mission_dir(mission_id) / "phase_ledger.jsonl"

    def _current_state_path(self, mission_id: str) -> Path:
        return self._mission_dir(mission_id) / "current_state.json"

    @contextmanager
    def _lock_ledger(self, mission_id: str, mode: str = "a+") -> Generator[Any, None, None]:
        path = self._ledger_path(mission_id)
        if mode == "r" and not path.exists():
            # Create if not exists to avoid open error for locking,
            # though iter_events handles non-existence before calling this.
            path.touch()

        with path.open(mode, encoding="utf-8") as handle:
            if fcntl:
                try:
                    # LOCK_EX for a+, LOCK_SH for r?
                    # For simplicity and to ensure idempotency check is consistent with write,
                    # we use LOCK_EX for both if we want to be safe, or LOCK_SH for read.
                    lock_type = fcntl.LOCK_EX if "w" in mode or "a" in mode or "+" in mode else fcntl.LOCK_SH
                    fcntl.flock(handle, lock_type)
                    yield handle
                finally:
                    fcntl.flock(handle, fcntl.LOCK_UN)
            else:
                logger.warning("fcntl not available, proceeding without file locking")
                yield handle

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

    def _write_text(self, path: Path, payload: str) -> None:
        self._reject_private(payload)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_name(f".{path.name}.tmp")
        tmp.write_text(payload, encoding="utf-8")
        with tmp.open("a", encoding="utf-8") as h:
            h.flush()
            try:
                os.fsync(h.fileno())
            except OSError:
                pass
        tmp.replace(path)

    def _validate_id(self, field_name: str, value: str) -> None:
        if not value or ".." in value or "/" in value or "\\" in value:
            raise ValueError(f"{field_name} rejected: path traversal is not allowed")
        if not _SAFE_ID.match(value):
            raise ValueError(f"{field_name} rejected: only letters, numbers, hyphen, and underscore are allowed")

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
                    raise ValueError(f"mission ledger payload contains {reason}")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _markdown_list(values: list[str]) -> str:
    if not values:
        return "- NONE"
    return "\n".join(f"- {value}" for value in values)

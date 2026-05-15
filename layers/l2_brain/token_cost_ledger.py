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

logger = logging.getLogger(__name__)

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


class TokenCostLedger:
    def __init__(self, root: str | Path = ".aiwg"):
        self.root = Path(root)

    def record_usage(self, event: dict) -> dict:
        session_id = str(event.get("session_id", ""))
        mission_id = str(event.get("mission_id", ""))
        phase_id = str(event.get("phase_id", ""))

        if mission_id:
            self._validate_id("mission_id", mission_id)
        if session_id:
            self._validate_id("session_id", session_id)
        if phase_id:
            self._validate_id("phase_id", phase_id)

        self._reject_private(event)

        event_id = event.get("event_id") or f"evt-{uuid.uuid4().hex}"
        timestamp = event.get("timestamp") or _now()

        normalized = {
            "event_id": event_id,
            "session_id": session_id,
            "mission_id": mission_id,
            "phase_id": phase_id,
            "model_tier": event.get("model_tier", "unknown"),
            "provider": event.get("provider", "unknown"),
            "source": event.get("source", "unknown"),
            "input_tokens": int(event.get("input_tokens") or 0),
            "cached_tokens": int(event.get("cached_tokens") or 0),
            "output_tokens": int(event.get("output_tokens") or 0),
            "reasoning_tokens": int(event.get("reasoning_tokens") or 0),
            "estimated": bool(event.get("estimated", False)),
            "timestamp": timestamp,
        }

        path = self._get_ledger_path(mission_id, session_id)
        path.parent.mkdir(parents=True, exist_ok=True)

        with self._lock_ledger(path) as handle:
            # Idempotency check
            handle.seek(0)
            for line in handle:
                if line.strip():
                    existing = json.loads(line)
                    if existing.get("event_id") == event_id:
                        return existing

            handle.seek(0, os.SEEK_END)
            handle.write(json.dumps(normalized, ensure_ascii=True, sort_keys=True) + "\n")
            handle.flush()
            try:
                os.fsync(handle.fileno())
            except OSError:
                pass

        return normalized

    def iter_usage(self, mission_id: str = "", session_id: str = "") -> Iterable[dict]:
        path = self._get_ledger_path(mission_id, session_id)
        if not path.exists():
            return iter(())

        def _reader():
            with self._lock_ledger(path, mode="r") as handle:
                for line in handle:
                    if line.strip():
                        yield json.loads(line)

        return _reader()

    def summarize_session(self, session_id: str) -> dict:
        return self._summarize(self.iter_usage(session_id=session_id))

    def summarize_mission(self, mission_id: str) -> dict:
        return self._summarize(self.iter_usage(mission_id=mission_id))

    def summarize_phase(self, mission_id: str, phase_id: str) -> dict:
        events = (e for e in self.iter_usage(mission_id=mission_id) if e.get("phase_id") == phase_id)
        return self._summarize(events)

    def cache_hit_ratio(self, mission_id: str = "", session_id: str = "") -> float:
        summary = self._summarize(self.iter_usage(mission_id, session_id))
        total_input = summary["total_input_tokens"] + summary["total_cached_tokens"]
        if total_input == 0:
            return 0.0
        return summary["total_cached_tokens"] / total_input

    def cloud_cost_estimate(self, mission_id: str = "", session_id: str = "") -> dict:
        # Placeholder for actual pricing logic
        summary = self._summarize(self.iter_usage(mission_id, session_id))
        return {
            "currency": "USD",
            "estimated_cost": 0.0,  # TODO: Implement pricing model
            "total_tokens": summary["total_tokens"],
        }

    def _summarize(self, events: Iterable[dict]) -> dict:
        summary = {
            "total_input_tokens": 0,
            "total_cached_tokens": 0,
            "total_output_tokens": 0,
            "total_reasoning_tokens": 0,
            "total_tokens": 0,
            "event_count": 0,
        }
        for event in events:
            summary["total_input_tokens"] += event.get("input_tokens", 0)
            summary["total_cached_tokens"] += event.get("cached_tokens", 0)
            summary["total_output_tokens"] += event.get("output_tokens", 0)
            summary["total_reasoning_tokens"] += event.get("reasoning_tokens", 0)
            summary["event_count"] += 1

        summary["total_tokens"] = (
            summary["total_input_tokens"]
            + summary["total_cached_tokens"]
            + summary["total_output_tokens"]
        )
        return summary

    def _get_ledger_path(self, mission_id: str = "", session_id: str = "") -> Path:
        if mission_id:
            self._validate_id("mission_id", mission_id)
            return self.root / "missions" / mission_id / "token_cost_ledger.jsonl"
        if session_id:
            self._validate_id("session_id", session_id)
            return self.root / "sessions" / session_id / "token_cost_ledger.jsonl"
        raise ValueError("Either mission_id or session_id must be provided")

    @contextmanager
    def _lock_ledger(self, path: Path, mode: str = "a+") -> Generator[Any, None, None]:
        if mode == "r" and not path.exists():
            path.touch()

        with path.open(mode, encoding="utf-8") as handle:
            if fcntl:
                try:
                    lock_type = (
                        fcntl.LOCK_EX
                        if "w" in mode or "a" in mode or "+" in mode
                        else fcntl.LOCK_SH
                    )
                    fcntl.flock(handle, lock_type)
                    yield handle
                finally:
                    fcntl.flock(handle, fcntl.LOCK_UN)
            else:
                yield handle

    def _validate_id(self, field_name: str, value: str) -> None:
        if not value or ".." in value or "/" in value or "\\" in value:
            raise ValueError(f"{field_name} rejected: path traversal is not allowed")
        if not _SAFE_ID.match(value):
            raise ValueError(
                f"{field_name} rejected: only letters, numbers, hyphen, and underscore are allowed"
            )

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
                    raise ValueError(f"token ledger payload contains {reason}")


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()

import datetime
import json
import re
from pathlib import Path
from typing import Any


class SessionStore:
    SESSION_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")

    def __init__(self, base_dir: str | Path):
        self.root_dir = Path(base_dir).resolve()
        self.base_dir = self.root_dir / ".aiwg" / "sessions"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def create_session(self, session_id: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        session_path = self._session_path(session_id)
        session_path.mkdir(parents=True, exist_ok=False)
        (session_path / "artifacts").mkdir(exist_ok=True)
        (session_path / "events.jsonl").touch(exist_ok=True)

        now = self._now()
        state = {
            "session_id": session_id,
            "created_at": now,
            "updated_at": now,
            "status": "active",
            "events_count": 0,
            "lamport_t": 0,
        }
        if metadata:
            state.update(metadata)
        self._write_json(session_path / "state.json", state)
        return self.load_session(session_id)

    def load_session(self, session_id: str) -> dict[str, Any]:
        session_path = self._session_path(session_id)
        if not session_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        state_path = session_path / "state.json"
        state = self._read_json(state_path) if state_path.exists() else {"session_id": session_id}
        events = self._read_events(session_path)
        artifacts_path = session_path / "artifacts"
        artifacts = sorted(path.name for path in artifacts_path.iterdir() if path.is_file())
        return {
            "session_id": session_id,
            "path": str(session_path),
            "state": state,
            "events": events,
            "artifacts": artifacts,
        }

    def save_state(self, session_id: str, state_update: dict[str, Any]) -> dict[str, Any]:
        session_path = self._session_path(session_id)
        if not session_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        state_path = session_path / "state.json"
        state = self._read_json(state_path)
        state.update(state_update)
        state["updated_at"] = self._now()
        self._write_json(state_path, state)
        return state

    def append_event(
        self,
        session_id: str,
        event_type: str,
        summary: str,
        data: dict[str, Any] | None = None,
        evidence_refs: list[str] | None = None,
        six_d_context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        session_path = self._session_path(session_id)
        if not session_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")

        state = self._read_json(session_path / "state.json")
        lamport_t = int(state.get("lamport_t", 0)) + 1
        event = {
            "event_type": event_type,
            "timestamp": self._now(),
            "summary": summary,
            "evidence_refs": evidence_refs or [],
            "six_d_context": six_d_context or {},
            "lamport_t": lamport_t,
            "data": data or {},
        }
        with (session_path / "events.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")

        state["events_count"] = int(state.get("events_count", 0)) + 1
        state["lamport_t"] = lamport_t
        state["updated_at"] = event["timestamp"]
        self._write_json(session_path / "state.json", state)
        return event

    def save_artifact(self, session_id: str, artifact_name: str, content: str) -> Path:
        session_path = self._session_path(session_id)
        if not session_path.exists():
            raise FileNotFoundError(f"Session not found: {session_id}")
        artifact_path = self._artifact_path(session_path, artifact_name)
        artifact_path.write_text(content, encoding="utf-8")
        return artifact_path

    def compact_session(self, session_id: str, keep_last: int = 10) -> dict[str, Any]:
        loaded = self.load_session(session_id)
        events = loaded["events"]
        retained = events[-keep_last:] if keep_last > 0 else []
        lines = [f"- t{event['lamport_t']} {event['event_type']}: {event['summary']}" for event in retained]
        summary = "\n".join(lines)
        self.save_artifact(session_id, "compact.md", f"# Session Compact\n\n{summary}\n")
        self.save_state(session_id, {"compacted_at": self._now(), "compacted_event_count": len(events)})
        return {"session_id": session_id, "summary": summary, "retained_events": retained}

    def list_sessions(self) -> list[dict[str, Any]]:
        sessions = []
        for path in sorted(self.base_dir.iterdir()):
            if path.is_dir() and (path / "state.json").exists():
                sessions.append(self._read_json(path / "state.json"))
        return sessions

    def _session_path(self, session_id: str) -> Path:
        self._validate_session_id(session_id)
        path = (self.base_dir / session_id).resolve()
        if not self._is_relative_to(path, self.base_dir):
            raise ValueError(f"Unsafe session_id: {session_id}")
        return path

    def _artifact_path(self, session_path: Path, artifact_name: str) -> Path:
        if not artifact_name or artifact_name != Path(artifact_name).name:
            raise ValueError(f"Unsafe artifact path: {artifact_name}")
        if artifact_name.startswith("."):
            raise ValueError(f"Unsafe artifact path: {artifact_name}")
        path = (session_path / "artifacts" / artifact_name).resolve()
        if not self._is_relative_to(path, session_path / "artifacts"):
            raise ValueError(f"Unsafe artifact path: {artifact_name}")
        return path

    def _validate_session_id(self, session_id: str) -> None:
        if not isinstance(session_id, str) or not self.SESSION_ID_RE.fullmatch(session_id):
            raise ValueError(f"Unsafe session_id: {session_id}")
        if session_id in {".", "..", ".git"}:
            raise ValueError(f"Unsafe session_id: {session_id}")

    @staticmethod
    def _read_json(path: Path) -> dict[str, Any]:
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    @staticmethod
    def _read_events(session_path: Path) -> list[dict[str, Any]]:
        events_path = session_path / "events.jsonl"
        if not events_path.exists():
            return []
        events = []
        for line in events_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                events.append(json.loads(line))
        return events

    @staticmethod
    def _now() -> str:
        return datetime.datetime.now(datetime.UTC).isoformat()

    @staticmethod
    def _is_relative_to(path: Path, parent: Path) -> bool:
        try:
            path.relative_to(parent.resolve())
            return True
        except ValueError:
            return False

import datetime
import json
import re
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any

try:
    import fcntl
except ImportError:  # Windows fallback
    fcntl = None


@contextmanager
def file_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock_file:
        if fcntl:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)


def atomic_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=str(path.parent),
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)

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

        lock_path = session_path / ".session.lock"

        with file_lock(lock_path):
            state_path = session_path / "state.json"
            state = self._read_json(state_path)
            lamport_t = int(state.get("lamport_t", 0)) + 1

            context = dict(six_d_context or {})
            context.setdefault("lamport_t", lamport_t)

            event = {
                "event_type": event_type,
                "timestamp": self._now(),
                "summary": summary,
                "evidence_refs": evidence_refs or [],
                "six_d_context": context,
                "lamport_t": lamport_t,
                "data": data or {},
            }

            with (session_path / "events.jsonl").open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(event, sort_keys=True) + "\n")
                handle.flush()
                os.fsync(handle.fileno())

            state["events_count"] = int(state.get("events_count", 0)) + 1
            state["lamport_t"] = lamport_t
            state["updated_at"] = event["timestamp"]
            self._write_json(state_path, state)

        return event

    def iter_events(self, session_id: str):
        session_path = self._session_path(session_id)
        events_path = session_path / "events.jsonl"
        if not events_path.exists():
            return
        with events_path.open("r", encoding="utf-8") as handle:
            for line_no, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    yield {
                        "event_type": "CORRUPT_EVENT_LINE",
                        "line_no": line_no,
                        "error": str(exc),
                    }

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
        atomic_write_text(
            path,
            json.dumps(data, indent=2, sort_keys=True) + "\n",
        )

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

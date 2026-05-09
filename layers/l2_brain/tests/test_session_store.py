import json
from pathlib import Path

import pytest

from session_store import SessionStore


def test_session_store_persists_state_events_artifacts_and_compaction(tmp_path):
    store = SessionStore(tmp_path)

    created = store.create_session("sess-1", metadata={"owner": "test"})
    assert created["state"]["session_id"] == "sess-1"
    assert (tmp_path / ".aiwg" / "sessions" / "sess-1").is_dir()

    state = store.save_state("sess-1", {"status": "planning", "mission_id": "miss_1"})
    assert state["status"] == "planning"

    first = store.append_event(
        "sess-1",
        "INTAKE",
        "Captured prompt.",
        evidence_refs=["prompt"],
        six_d_context={"axis": "runtime"},
    )
    second = store.append_event("sess-1", "PLAN", "Planned next action.")
    assert first["event_type"] == "INTAKE"
    assert first["lamport_t"] == 1
    assert second["lamport_t"] == 2

    artifact = store.save_artifact("sess-1", "intake.md", "# Intake\n")
    assert artifact.name == "intake.md"

    compacted = store.compact_session("sess-1", keep_last=1)
    assert "Planned next action." in compacted["summary"]

    loaded = store.load_session("sess-1")
    assert loaded["state"]["events_count"] == 2
    assert loaded["events"][0]["evidence_refs"] == ["prompt"]
    assert loaded["artifacts"] == ["compact.md", "intake.md"]
    assert store.list_sessions()[0]["session_id"] == "sess-1"

    event_lines = (tmp_path / ".aiwg" / "sessions" / "sess-1" / "events.jsonl").read_text().splitlines()
    assert json.loads(event_lines[0])["six_d_context"]["axis"] == "runtime"


@pytest.mark.parametrize(
    "unsafe",
    ["../escape", "nested/session", "/abs", "a\\b", ".git", ""],
)
def test_session_store_rejects_path_traversal_session_ids(tmp_path, unsafe):
    store = SessionStore(tmp_path)

    with pytest.raises(ValueError):
        store.create_session(unsafe)


@pytest.mark.parametrize("unsafe_artifact", ["../x.md", "/tmp/x.md", ".git/config", "nested/x.md"])
def test_session_store_rejects_artifact_path_traversal(tmp_path, unsafe_artifact):
    store = SessionStore(tmp_path)
    store.create_session("safe")

    with pytest.raises(ValueError):
        store.save_artifact("safe", unsafe_artifact, "blocked")

from __future__ import annotations

import json
from pathlib import Path

import pytest
from memory_spine_bridge import MemorySpineBridge
from session_store import SessionStore


@pytest.fixture
def temp_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    aiwg = repo / ".aiwg"
    aiwg.mkdir()
    (aiwg / "sessions").mkdir()
    (aiwg / "reports").mkdir()
    (aiwg / "memory").mkdir()
    return repo


def test_memory_spine_sync_flow(temp_repo):
    # 1. Setup session with learning episode
    store = SessionStore(temp_repo)
    sid = "test-session-1"
    store.create_session(sid)
    
    episode = {
        "episode_id": "ep-123",
        "mission_id": "mission-alpha",
        "outcome": "SUCCESS",
        "capability_amplification_score": 0.8
    }
    store.append_learning_episode(sid, episode)
    
    # 2. Run Bridge
    bridge = MemorySpineBridge(repo_root=temp_repo, aiwg_root=".aiwg")
    summary = bridge.sync_all_sessions(allow_write=False)
    
    # 3. Validate summary
    assert summary["decision"] == "PASS"
    assert summary["sessions_synced"] == 1
    assert summary["total_nodes"] == 1
    
    # Check report exists
    report_path = temp_repo / ".aiwg" / "reports" / "memory_spine_sync_latest.json"
    assert report_path.exists()
    
    report = json.loads(report_path.read_text())
    assert report["total_nodes"] == 1


def test_memory_spine_sync_no_episodes(temp_repo):
    store = SessionStore(temp_repo)
    sid = "empty-session"
    store.create_session(sid)
    
    bridge = MemorySpineBridge(repo_root=temp_repo, aiwg_root=".aiwg")
    summary = bridge.sync_all_sessions(allow_write=False)
    
    assert summary["sessions_synced"] == 1
    assert summary["total_nodes"] == 0

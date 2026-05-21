"""Tests for MemorySpineEntrypoint — Pack 3 Module 2."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
L2 = ROOT / "layers" / "l2_brain"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(L2) not in sys.path:
    sys.path.insert(0, str(L2))

from layers.l2_brain.memory.memory_spine_entrypoint import (
    MemorySpineEntrypoint,
    MemorySpineRetrievalResult,
    MemorySpineQuery,
    retrieve_memory_for_intent,
    run_memory_spine_entrypoint_demo,
)


@pytest.fixture
def aiwg_dir(tmp_path):
    aiwg = tmp_path / ".aiwg"
    reports = aiwg / "reports"
    reports.mkdir(parents=True)
    sessions = aiwg / "sessions"
    sessions.mkdir(parents=True)
    return aiwg


class TestMemorySpineEntrypoint:
    def test_returns_degraded_when_kuzu_unavailable(self, aiwg_dir):
        """Must return DEGRADED_WITH_FILE_BACKED_MEMORY when Kuzu DEGRADED."""
        reports = aiwg_dir / "reports"
        (reports / "memory_spine_sync_latest.json").write_text(
            json.dumps({"db_status": "DEGRADED"}), encoding="utf-8"
        )
        ep = MemorySpineEntrypoint(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        result = ep.retrieve_memory_for_intent("status")

        assert result.status == "DEGRADED_WITH_FILE_BACKED_MEMORY"
        assert result.graph_status == "DEGRADED"
        assert result.decision == "PASS_WITH_WARNINGS"
        assert any("DEGRADED" in w for w in result.warnings)

    def test_returns_ready_when_kuzu_ok(self, aiwg_dir):
        """Must return READY when no degradation detected."""
        reports = aiwg_dir / "reports"
        (reports / "memory_spine_sync_latest.json").write_text(
            json.dumps({"db_status": "READY"}), encoding="utf-8"
        )
        ep = MemorySpineEntrypoint(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        result = ep.retrieve_memory_for_intent("status")

        assert result.status == "READY"

    def test_writes_latest_json(self, aiwg_dir):
        """Must write memory_spine_entrypoint_latest.json."""
        ep = MemorySpineEntrypoint(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        ep.retrieve_memory_for_intent("test")

        path = aiwg_dir / "reports" / "memory_spine_entrypoint_latest.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "decision" in data
        assert data["used_before_chat_response"] is True

    def test_vault_scan(self, aiwg_dir):
        """Should find vault entries matching keywords."""
        vault = aiwg_dir / "vault"
        vault.mkdir(parents=True)
        (vault / "entry1.json").write_text(
            json.dumps({"topic": "deployment strategy", "content": "use canary releases"}),
            encoding="utf-8"
        )
        ep = MemorySpineEntrypoint(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        result = ep.retrieve_memory_for_intent("deployment")

        assert len(result.vault_refs) > 0

    def test_used_before_chat_response_always_true(self, aiwg_dir):
        """Must always set used_before_chat_response to True."""
        ep = MemorySpineEntrypoint(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        result = ep.retrieve_memory_for_intent("anything")
        assert result.used_before_chat_response is True

    def test_to_dict(self, aiwg_dir):
        """Result must be serializable."""
        ep = MemorySpineEntrypoint(repo_root=aiwg_dir.parent, aiwg_root=".aiwg")
        result = ep.retrieve_memory_for_intent("test")
        d = result.to_dict()
        assert isinstance(d, dict)
        json.dumps(d)  # Must not raise

    def test_run_demo(self, aiwg_dir, monkeypatch):
        """run_memory_spine_entrypoint_demo should return MemorySpineRetrievalResult."""
        monkeypatch.chdir(aiwg_dir.parent)
        result = run_memory_spine_entrypoint_demo("test", repo_root=aiwg_dir.parent)
        assert isinstance(result, MemorySpineRetrievalResult)

    def test_memory_spine_query_dataclass(self):
        """MemorySpineQuery should be constructible."""
        q = MemorySpineQuery(intent="test", keywords=["a", "b"])
        assert q.intent == "test"

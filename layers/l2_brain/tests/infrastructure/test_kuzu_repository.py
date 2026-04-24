import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters import KuzuRepository


class _FakeConn:
    def __init__(self):
        self.cypher = []

    def execute(self, cypher: str):
        self.cypher.append(cypher)
        return {"ok": True}


class _FakeIPCBridge:
    def __init__(self):
        self.ipc = _FakeConn()


def test_repository_uses_ipc_connection_when_bridge_exposes_ipc():
    bridge = _FakeIPCBridge()
    repo = KuzuRepository(db=bridge)
    result = repo.query("MATCH (n) RETURN count(n)")
    assert result == {"ok": True}
    assert repo.conn is bridge.ipc
    assert bridge.ipc.cypher == ["MATCH (n) RETURN count(n)"]


def test_repository_returns_empty_without_connection():
    repo = KuzuRepository(db_path="/tmp/unused.db", db=None)
    assert repo.query("RETURN 1") == []

import pytest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from adapters import (
    KuzuRepository,
    KuzuSkillRepository,
    DecisionLedgerAdapter,
    SessionLedgerAdapter,
    NativeShieldAdapter,
)
from orchestrator import CognitiveOrchestrator


@pytest.fixture
def clean_env(tmp_path):
    ledger_path = str(tmp_path / "resolutions.jsonl")
    session_path = str(tmp_path / "session.jsonl")
    repo = KuzuRepository(db_path=str(tmp_path / "loci.db"), db=None)
    skill_repo = KuzuSkillRepository(db_path=str(tmp_path / "skills.db"), db=None)
    ledger = DecisionLedgerAdapter(
        ledger_path=ledger_path,
        lessons_path=str(tmp_path / "lessons.jsonl"),
        ambiguities_path=str(tmp_path / "ambiguities.jsonl"),
        ontological_map_path=str(tmp_path / "ontological_map.json"),
    )
    session = SessionLedgerAdapter(ledger_path=session_path)
    shield = NativeShieldAdapter()
    orchestrator = CognitiveOrchestrator(
        shield_port=shield,
        event_store=repo,
        ledger_audit=ledger,
        session_ledger=session,
        skill_repo=skill_repo,
    )
    return {"orchestrator": orchestrator, "repo": repo, "ledger": ledger, "paths": {"ledger": ledger_path}}


class _Intent:
    def __init__(self, goal: str):
        self.goal = goal


@pytest.mark.asyncio
async def test_bridge_orchestrator_acknowledges_intent(clean_env):
    result = await clean_env["orchestrator"].process_intent(_Intent("Industrialize gateway path"))
    assert result["status"] == "ACK"
    assert result["intent_id"] == "LEGACY-01"


def test_decision_ledger_adapter_persists_jsonl(clean_env):
    entry = {"tick": 1, "impact": "LOW", "goal": "Test write"}
    clean_env["ledger"].log_resolution(entry)
    with open(clean_env["paths"]["ledger"], "r", encoding="utf-8") as fh:
        raw = fh.readline().strip()
    assert "\"tick\": 1" in raw
    assert "\"impact\": \"LOW\"" in raw


@pytest.mark.asyncio
async def test_native_shield_adapter_allows_by_default(clean_env):
    ok, msg = await NativeShieldAdapter().audit("<dag></dag>", "test")
    assert ok is True
    assert msg == "BYPASS"

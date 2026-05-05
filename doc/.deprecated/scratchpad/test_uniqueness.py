import os
import sys
import asyncio

# Set up PYTHONPATH
sys.path.append("/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain/src")

from brain.infrastructure.adapters.kuzu_repository import KuzuRepository
from brain.infrastructure.adapters.ledger_adapter import DecisionLedgerAdapter
from brain.infrastructure.adapters.session_ledger_adapter import SessionLedgerAdapter
from brain.infrastructure.adapters.shield_adapter import NativeShieldAdapter
from brain.infrastructure.adapters.skill_adapter import KuzuSkillRepository
from brain.application.use_cases.orchestrator import CognitiveOrchestrator
from brain.domain.fabrication.models import AgentIntent, IntentType as FabricationIntent
from brain.domain.context.models import AuthorityLevel, IntentType as ContextIntent
import kuzu

KUZU_DB_PATH = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/loci.db"
AIWG_DIR = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg"

async def test_uniqueness():
    db = kuzu.Database(KUZU_DB_PATH)
    event_store = KuzuRepository(db_path=KUZU_DB_PATH, db=db)
    ledger_audit = DecisionLedgerAdapter(
        ledger_path=os.path.join(AIWG_DIR, "ledger/sovereign_resolutions.jsonl"),
        lessons_path=os.path.join(AIWG_DIR, "memory/lessons.jsonl"),
        ambiguities_path=os.path.join(AIWG_DIR, "memory/ambiguities.jsonl"),
        ontological_map_path=os.path.join(AIWG_DIR, "ontological_map.json")
    )
    session_ledger = SessionLedgerAdapter(ledger_path=os.path.join(AIWG_DIR, "memory/ego_state.jsonl"))
    shield = NativeShieldAdapter()
    skill_repo = KuzuSkillRepository(db_path=KUZU_DB_PATH, db=db)

    orchestrator = CognitiveOrchestrator(
        shield_port=shield,
        event_store=event_store,
        ledger_audit=ledger_audit,
        session_ledger=session_ledger,
        skill_repo=skill_repo
    )
    
    print(f"Start Clock: {orchestrator.lamport_clock}")
    
    intent1 = AgentIntent(
        intent_type=FabricationIntent.RESOLUTION,
        target="TEST_TARGET",
        rationale="Payload Alpha",
        risk_score=0.1
    )
    
    res1 = await orchestrator.handle_task(intent1)
    print(f"Task 1: {res1}, Clock now: {orchestrator.lamport_clock}")
    
    intent2 = AgentIntent(
        intent_type=FabricationIntent.RESOLUTION,
        target="TEST_TARGET",
        rationale="Payload Beta",
        risk_score=0.1
    )
    
    res2 = await orchestrator.handle_task(intent2)
    print(f"Task 2: {res2}, Clock now: {orchestrator.lamport_clock}")

if __name__ == "__main__":
    asyncio.run(test_uniqueness())

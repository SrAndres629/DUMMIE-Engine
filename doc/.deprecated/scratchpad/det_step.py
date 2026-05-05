import asyncio
import os
import sys

# Set up PYTHONPATH
sys.path.append("/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain/src")

from brain.infrastructure.adapters.kuzu_repository import KuzuRepository
from brain.infrastructure.adapters.ledger_adapter import DecisionLedgerAdapter
from brain.infrastructure.adapters.session_ledger_adapter import SessionLedgerAdapter
from brain.infrastructure.adapters.shield_adapter import NativeShieldAdapter
from brain.infrastructure.adapters.skill_adapter import KuzuSkillRepository
from brain.application.use_cases.orchestrator import CognitiveOrchestrator
from brain.domain.fabrication.models import AgentIntent, IntentType
import kuzu

KUZU_DB_PATH = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/loci.db"
AIWG_DIR = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg"

async def run_step():
    db = kuzu.Database(KUZU_DB_PATH)
    event_store = KuzuRepository(db_path=KUZU_DB_PATH, db=db)
    ledger_audit = DecisionLedgerAdapter(
        ledger_path=os.path.join(AIWG_DIR, "ledger/sovereign_resolutions.jsonl"),
        lessons_path=os.path.join(AIWG_DIR, "memory/lessons.jsonl"),
        ambiguities_path=os.path.join(AIWG_DIR, "memory/ambiguities.jsonl"),
        ontological_map_path=os.path.join(AIWG_DIR, "ontological_map.json")
    )
    session_ledger = SessionLedgerAdapter(ledger_path=os.path.join(AIWG_DIR, "memory/ego_state.jsonl"))
    skill_repo = KuzuSkillRepository(db_path=KUZU_DB_PATH, db=db)
    
    orch = CognitiveOrchestrator(
        shield_port=NativeShieldAdapter(),
        event_store=event_store,
        ledger_audit=ledger_audit,
        session_ledger=session_ledger,
        skill_repo=skill_repo
    )
    
    tick = orch.lamport_clock
    intent = AgentIntent(intent_type=IntentType.RESOLUTION, target="DET_TEST", rationale=f"Step at {tick}", risk_score=0.1)
    await orch.handle_task(intent)
    
    leaf_hash = event_store.get_last_leaf_hash()
    last_node = event_store.get_by_hash(leaf_hash)
    print(f"HASH:{last_node.causal_hash}|PARENT:{last_node.parent_hash}|TICK:{last_node.context.lamport_t}")

if __name__ == "__main__":
    asyncio.run(run_step())

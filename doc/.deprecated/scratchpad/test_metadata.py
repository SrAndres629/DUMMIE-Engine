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
from brain.domain.context.models import SixDimensionalContext, AuthorityLevel, IntentType as ContextIntent
import kuzu

KUZU_DB_PATH = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/loci.db"
AIWG_DIR = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg"

def test_metadata():
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
    
    context = SixDimensionalContext(
        locus_x="sw.strategy.discovery",
        locus_y="TEST",
        locus_z="TEST",
        lamport_t=orchestrator.lamport_clock,
        authority_a=AuthorityLevel.AGENT,
        intent_i=ContextIntent.OBSERVATION
    )
    
    # Test Lesson
    orchestrator.lessons_use_case.execute_error(
        context=context,
        error=Exception("Test Error"),
        tick=orchestrator.lamport_clock,
        correction="Real Correction",
        prevention="Real Prevention"
    )
    
    # Test Ambiguity
    orchestrator.lessons_use_case.execute_ambiguity(
        context=context,
        ambiguity="Critical security vulnerability found",
        plan="Fix it immediately"
    )
    
    print("Lesson and Ambiguity recorded.")

if __name__ == "__main__":
    test_metadata()

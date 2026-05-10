import asyncio
import os
import sys
import hashlib

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

async def stress_test_determinism():
    print("--- INICIANDO AUDITORÍA ESTRUCTURAL DE DETERMINISMO ---")
    
    # 1. Primera Sesión
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
    
    orch1 = CognitiveOrchestrator(
        shield_port=NativeShieldAdapter(),
        event_store=event_store,
        ledger_audit=ledger_audit,
        session_ledger=session_ledger,
        skill_repo=skill_repo
    )
    
    t1 = orch1.lamport_clock
    print(f"Sesión 1 - Reloj Inicial: {t1}")
    
    intent1 = AgentIntent(intent_type=IntentType.RESOLUTION, target="DET_TEST", rationale=f"R-{t1}", risk_score=0.1)
    await orch1.handle_task(intent1)
    
    last_node1 = event_store.get_latest_node()
    h1 = last_node1.causal_hash
    print(f"Sesión 1 - Nodo Generado: {h1} (Clock: {last_node1.context.lamport_t})")
    
    # Cerrar DB simulando reinicio
    del orch1
    del event_store
    del db
    
    # 2. Segunda Sesión (Post-Reinicio)
    db2 = kuzu.Database(KUZU_DB_PATH)
    event_store2 = KuzuRepository(db_path=KUZU_DB_PATH, db=db2)
    orch2 = CognitiveOrchestrator(
        shield_port=NativeShieldAdapter(),
        event_store=event_store2,
        ledger_audit=ledger_audit,
        session_ledger=session_ledger,
        skill_repo=KuzuSkillRepository(db_path=KUZU_DB_PATH, db=db2)
    )
    
    t2 = orch2.lamport_clock
    print(f"Sesión 2 - Reloj Recuperado: {t2}")
    
    if t2 <= t1:
        print(f"❌ FALLO DE DETERMINISMO: El reloj no avanzó ({t2} <= {t1})")
        return
    
    intent2 = AgentIntent(intent_type=IntentType.RESOLUTION, target="DET_TEST", rationale=f"R-{t2}", risk_score=0.1)
    await orch2.handle_task(intent2)
    
    last_node2 = event_store2.get_latest_node()
    h2 = last_node2.causal_hash
    p2 = last_node2.parent_hash
    
    print(f"Sesión 2 - Nodo Generado: {h2}")
    print(f"Sesión 2 - Puntero Parent: {p2}")
    
    if p2 == h1:
        print("✅ ÉXITO: El encadenamiento causal es íntegro a través de reinicios.")
    else:
        print(f"❌ FALLO: El parent_hash ({p2}) no coincide con el nodo anterior ({h1}).")

if __name__ == "__main__":
    asyncio.run(stress_test_determinism())

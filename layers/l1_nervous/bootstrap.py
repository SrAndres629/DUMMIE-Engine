import os
import sys
import logging
import atexit
import signal
from pathlib import Path

# [TABULA RASA v2] Redirección Nerviosa a L2 Plana
try:
    from layers.l2_brain.models import SixDimensionalContext, AuthorityLevel, IntentType as ContextIntent
    from layers.l2_brain.models import AgentIntent, IntentType as FabricationIntent
    from layers.l2_brain.src.brain.application.use_cases.orchestrator import CognitiveOrchestrator
    from layers.l2_brain.adapters import KuzuRepository, DecisionLedgerAdapter, SessionLedgerAdapter, NativeShieldAdapter, KuzuSkillRepository
except ImportError:
    # Intento de redundancia si no está en PYTHONPATH directo
    ROOT_DIR = os.environ.get("DUMMIE_ROOT", os.environ.get("DUMMIE_ROOT_DIR", ""))
    if ROOT_DIR:
        if ROOT_DIR not in sys.path:
            sys.path.append(ROOT_DIR)
        l2_path = os.path.join(ROOT_DIR, "layers/l2_brain")
        if l2_path not in sys.path:
            sys.path.append(l2_path)
    
    from models import SixDimensionalContext, AuthorityLevel, IntentType as ContextIntent
    from models import AgentIntent, IntentType as FabricationIntent
    from src.brain.application.use_cases.orchestrator import CognitiveOrchestrator
    from adapters import KuzuRepository, DecisionLedgerAdapter, SessionLedgerAdapter, NativeShieldAdapter, KuzuSkillRepository

logger = logging.getLogger("dummie-mcp.infra")

def bootstrap_orchestrator(kuzu_db_path: str, aiwg_dir: str):
    db = None
    read_only = False

    # [TABULA RASA v2] Inicialización NATIVA directa (Wave 1 Fix)
    # Ignoramos el ArrowMemoryBridge y usamos Kuzu directamente.
    # El KuzuRepository ahora tiene safe_init_or_recover() para lidiar con locks
    try:
        logger.info(f"Inicializando 4D-TES (Kuzu) en modo nativo en {kuzu_db_path}")
        event_store = KuzuRepository(db_path=kuzu_db_path)
        db = event_store.db
    except Exception as e:
        logger.error(f"Fallo crítico al inicializar 4D-TES en modo nativo: {e}")
        event_store = KuzuRepository() # Modo stub
        event_store.read_only = True
        read_only = True
        
    ledger_audit = DecisionLedgerAdapter(
        ledger_path=os.path.join(aiwg_dir, "ledger/sovereign_resolutions.jsonl"),
        lessons_path=os.path.join(aiwg_dir, "memory/lessons.jsonl"),
        ambiguities_path=os.path.join(aiwg_dir, "memory/ambiguities.jsonl"),
        ontological_map_path=os.path.join(aiwg_dir, "ontological_map.json")
    )
    session_ledger = SessionLedgerAdapter(ledger_path=os.path.join(aiwg_dir, "memory/ego_state.jsonl"))
    shield = NativeShieldAdapter()
    
    # Compartir el objeto 'db' para evitar bloqueos por doble apertura
    skill_repo = KuzuSkillRepository(db=db)
    if read_only or db is None:
        skill_repo.read_only = True

    return CognitiveOrchestrator(
        shield_port=shield,
        event_store=event_store,
        ledger_audit=ledger_audit,
        session_ledger=session_ledger,
        skill_repo=skill_repo
    )

def setup_shutdown_handlers(orchestrator, proxy_manager=None):
    def _mcp_shutdown():
        try:
            import asyncio
            if proxy_manager:
                asyncio.run(proxy_manager.shutdown())
        except:
            pass

    atexit.register(_mcp_shutdown)
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0))
    signal.signal(signal.SIGINT, lambda *_: sys.exit(0))

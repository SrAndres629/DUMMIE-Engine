import os
import sys
import logging
import atexit
import signal
from pathlib import Path

# [TABULA RASA v2] Redirección Nerviosa a L2 Plana
try:
    from models import SixDimensionalContext, AuthorityLevel, IntentType as ContextIntent
    from models import AgentIntent, IntentType as FabricationIntent
    from orchestrator import CognitiveOrchestrator
    from adapters import KuzuRepository, DecisionLedgerAdapter, SessionLedgerAdapter, NativeShieldAdapter, KuzuSkillRepository
except ImportError:
    # Intento de redundancia si no está en PYTHONPATH directo
    sys.path.append(os.path.join(os.environ.get("DUMMIE_ROOT", os.environ.get("DUMMIE_ROOT_DIR", "")), "layers/l2_brain"))
    from models import SixDimensionalContext, AuthorityLevel, IntentType as ContextIntent
    from models import AgentIntent, IntentType as FabricationIntent
    from orchestrator import CognitiveOrchestrator
    from adapters import KuzuRepository, DecisionLedgerAdapter, SessionLedgerAdapter, NativeShieldAdapter, KuzuSkillRepository

logger = logging.getLogger("dummie-mcp.infra")

def bootstrap_orchestrator(kuzu_db_path: str, aiwg_dir: str):
    from memory_ipc import ArrowMemoryBridge
    
    db = None
    read_only = False

    # [SPEC-30] Intento de conexión al Memory Plane (Zero-Copy IPC)
    bridge = ArrowMemoryBridge() # Ahora usa defaults normalizados
    if bridge.heartbeat():
        logger.info(f"Memory Plane active and verified at {bridge.socket_path}. Activating IPC mode.")
        db = bridge
    else:
        logger.error(f"Memory Plane OFFLINE at {bridge.socket_path}. Entering DEGRADED mode.")
        logger.warning("[!] ADVERTENCIA: El Memory Plane (L0) no está activo.")
        logger.warning("    El sistema arrancará en modo DEGRADADO (sin persistencia).")
        db = None

    event_store = KuzuRepository(db_path=kuzu_db_path if db else None, db=db)
    if read_only or db is None:
        event_store.read_only = True
        
    ledger_audit = DecisionLedgerAdapter(
        ledger_path=os.path.join(aiwg_dir, "ledger/sovereign_resolutions.jsonl"),
        lessons_path=os.path.join(aiwg_dir, "memory/lessons.jsonl"),
        ambiguities_path=os.path.join(aiwg_dir, "memory/ambiguities.jsonl"),
        ontological_map_path=os.path.join(aiwg_dir, "ontological_map.json")
    )
    session_ledger = SessionLedgerAdapter(ledger_path=os.path.join(aiwg_dir, "memory/ego_state.jsonl"))
    shield = NativeShieldAdapter()
    
    skill_repo = KuzuSkillRepository(db_path=kuzu_db_path if db else None, db=db)
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

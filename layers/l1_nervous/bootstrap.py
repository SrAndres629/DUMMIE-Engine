# Spec Reference: 15_mcp_sidecar_isolation
import os
import sys
import logging
import atexit
import signal
from pathlib import Path

# [TABULA RASA v2] Redirección Nerviosa a L2
from layers.l2_brain.l2_memory_models import (
    SixDimensionalContext,
    AuthorityLevel,
    IntentType as ContextIntent,
)
from layers.l2_brain.l2_memory_models import AgentIntent, IntentType as FabricationIntent
from layers.l2_brain.adapters import (
    KuzuRepository,
    DecisionLedgerAdapter,
    SessionLedgerAdapter,
    NativeShieldAdapter,
    KuzuSkillRepository,
)
from layers.l2_brain.src.brain.application.use_cases.orchestrator import (
    CognitiveOrchestrator,
)

logger = logging.getLogger("dummie-mcp.infra")


from layers.l2_brain.infrastructure.supervisor import ProcessSupervisor

import kuzu


# ...
def bootstrap_orchestrator(kuzu_db_path: str, aiwg_dir: str):
    # Step 1: Open kuzu.Database once, handle lock/read_only
    db = None
    read_only = False
    try:
        db = kuzu.Database(kuzu_db_path)
    except RuntimeError as e:
        if "Could not set lock on file" in str(e):
            db = kuzu.Database(kuzu_db_path, read_only=True)
            read_only = True
        else:
            raise

    # Step 2: Create all adapters sharing the same `db` object
    event_store = KuzuRepository(db_path=kuzu_db_path, db=db)
    if read_only:
        event_store.read_only = True

    ledger_audit = DecisionLedgerAdapter(
        ledger_path=os.path.join(aiwg_dir, "ledger/sovereign_resolutions.jsonl"),
        lessons_path=os.path.join(aiwg_dir, "memory/lessons.jsonl"),
        ambiguities_path=os.path.join(aiwg_dir, "memory/ambiguities.jsonl"),
        ontological_map_path=os.path.join(aiwg_dir, "ontological_map.json"),
    )

    session_ledger = SessionLedgerAdapter(
        ledger_path=os.path.join(aiwg_dir, "memory/ego_state.jsonl")
    )

    shield = NativeShieldAdapter()
    supervisor = ProcessSupervisor()

    skill_repo = KuzuSkillRepository(db_path=kuzu_db_path, db=db)
    if read_only:
        skill_repo.read_only = True

    return CognitiveOrchestrator(
        shield_port=shield,
        event_store=event_store,
        ledger_audit=ledger_audit,
        session_ledger=session_ledger,
        skill_repo=skill_repo,
        supervisor=supervisor,
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

import os
import json
import logging
import fcntl
from typing import Dict, Any, List, Optional

logger = logging.getLogger("brain.adapters")

class KuzuRepository:
    def __init__(self, db_path: Optional[str] = None, db: Any = None):
        self.db = db
        self.read_only = False
        self.conn = None
        if db:
            if hasattr(db, "ipc"):
                # [SPEC-30] Memory Plane (Arrow IPC)
                # Obtenemos el proxy de conexión directamente
                self.conn = db.ipc
                logger.info("KuzuRepository initialized in IPC mode (Zero-Copy)")
            else:
                # Modo Nativo
                import kuzu
                self.conn = kuzu.Connection(db)

    def query(self, cypher: str):
        if not self.conn: return []
        if hasattr(self.conn, "execute"):
            return self.conn.execute(cypher)
        return []

class DecisionLedgerAdapter:
    def __init__(self, ledger_path: str, lessons_path: str, ambiguities_path: str, ontological_map_path: str):
        self.ledger_path = ledger_path
        self.lessons_path = lessons_path
        self.ambiguities_path = ambiguities_path
        self.ontological_map_path = ontological_map_path

    def log_resolution(self, entry: Dict[str, Any]):
        with open(self.ledger_path, "a") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def log_lesson(self, entry: Dict[str, Any]):
        with open(self.lessons_path, "a") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

    def log_ambiguity(self, entry: Dict[str, Any]):
        with open(self.ambiguities_path, "a") as f:
            try:
                fcntl.flock(f, fcntl.LOCK_EX)
                f.write(json.dumps(entry) + "\n")
            finally:
                fcntl.flock(f, fcntl.LOCK_UN)

class SessionLedgerAdapter:
    def __init__(self, ledger_path: str):
        self.ledger_path = ledger_path

class NativeShieldAdapter:
    """Mock/Stub de compatibilidad para el bootstrap antiguo."""
    async def audit(self, dag, goal):
        return True, "BYPASS"

class KuzuSkillRepository(KuzuRepository):
    pass

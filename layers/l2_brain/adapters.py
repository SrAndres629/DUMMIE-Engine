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
            import kuzu
            self.conn = kuzu.Connection(db)

    def query(self, cypher: str):
        if not self.conn: return []
        return self.conn.execute(cypher)

class DecisionLedgerAdapter:
    def __init__(self, ledger_path: str, lessons_path: str, ambiguities_path: str, ontological_map_path: str):
        self.ledger_path = ledger_path
        self.lessons_path = lessons_path

    def log_resolution(self, entry: Dict[str, Any]):
        with open(self.ledger_path, "a") as f:
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

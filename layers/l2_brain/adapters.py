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
                self.conn = db.ipc
                logger.info("KuzuRepository initialized in IPC mode (Zero-Copy)")
            else:
                # Modo Nativo
                import kuzu
                self.conn = kuzu.Connection(db)
        elif db_path:
            import kuzu
            # Asegurar que el path sea un directorio
            if os.path.exists(db_path) and os.path.isfile(db_path):
                logger.warning(f"Removing file {db_path} to create Kuzu directory")
                os.remove(db_path)
            self.db = kuzu.Database(db_path)
            self.conn = kuzu.Connection(self.db)
            self._ensure_schema()

    def _ensure_schema(self):
        """Crea las tablas necesarias si no existen."""
        if not self.conn: return
        try:
            self.conn.execute("CREATE NODE TABLE MemoryNode4D(causal_hash STRING, parent_hash STRING, lamport_t INT64, locus_x STRING, locus_y STRING, locus_z STRING, authority_a STRING, intent_i STRING, summary STRING, timestamp INT64, PRIMARY KEY (causal_hash))")
            logger.info("Created table MemoryNode4D")
        except Exception:
            pass # Ya existe

    def query(self, cypher: str):
        if not self.conn: return []
        return self.conn.execute(cypher)

    def get_last_leaf_hash(self) -> str:
        res = self.query("MATCH (m:MemoryNode4D) RETURN m.causal_hash ORDER BY m.lamport_t DESC LIMIT 1")
        if res.has_next():
            return res.get_next()[0]
        return "GENESIS"

    def get_by_hash(self, causal_hash: str) -> Any:
        res = self.query(f"MATCH (m:MemoryNode4D) WHERE m.causal_hash = '{causal_hash}' RETURN m.*")
        if res.has_next():
            row = res.get_next()
            # Retornar un objeto mock que se parezca a lo que esperan los tests
            class Node: pass
            n = Node()
            n.causal_hash = row[0]
            n.parent_hash = row[1]
            class Context: pass
            n.context = Context()
            n.context.lamport_t = row[2]
            n.locus_x = row[3]
            n.locus_y = row[4]
            n.locus_z = row[5]
            n.authority_a = row[6]
            n.intent_i = row[7]
            n.summary = row[8]
            n.timestamp = row[9]
            return n
        return None

    def get_causal_chain(self, leaf_hash: str) -> List[Any]:
        chain = []
        current = leaf_hash
        while current and current != "GENESIS":
            node = self.get_by_hash(current)
            if not node: break
            chain.append(node)
            current = node.parent_hash
        return chain

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

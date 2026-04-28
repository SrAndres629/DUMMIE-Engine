import os
import json
import logging
import fcntl
from typing import Dict, Any, List, Optional
try:
    from layers.l2_brain.ports import CodeAnalysisPort, ObservabilityPort
except ModuleNotFoundError:
    from ports import CodeAnalysisPort, ObservabilityPort

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
            # [HARDENING] Verificación de integridad de ruta
            # Kùzu espera que el path sea el nombre de la base de datos (archivo o prefijo),
            # NO un directorio ya existente (en algunas versiones).
            if os.path.isdir(db_path):
                # Si es un directorio, verificamos si contiene archivos de Kùzu.
                # Si está vacío o no parece una DB, lanzamos error para evitar confusión.
                if not os.listdir(db_path):
                    logger.error(f"CRITICAL: Kuzu path '{db_path}' is an empty directory. Kuzu requires the path to be the database target, not a pre-existing directory.")
                    raise ValueError(f"Invalid Kuzu database path: '{db_path}' is a directory. Provide a file-like path.")
            
            # Asegurar que el directorio PADRE exista
            parent_dir = os.path.dirname(os.path.abspath(db_path))
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                logger.info(f"Created parent directory for Kuzu: {parent_dir}")
            
            self.db = kuzu.Database(db_path)
            self.conn = kuzu.Connection(self.db)
            logger.warning("[!] ALERTA DE SOBERANÍA: KuzuRepository ha inicializado en Modo NATIVO (Lock físico).")
            logger.warning("    Esto impide que otros agentes se conecten concurrentemente. Se recomienda usar IPC Singleton.")
            self._ensure_schema()

    def _ensure_schema(self):
        """Crea las tablas necesarias si no existen con el esquema SOVEREIGN-4D."""
        if not self.conn: return
        try:
            from models import MemoryNode4D
            # Esquema alineado con .aiwg/memory/loci.db real
            self.conn.execute(MemoryNode4D.schema_creation_query())
            logger.info("Created table MemoryNode4D with SOVEREIGN-4D schema")
        except Exception as e:
            # Solo permitimos pasar si el error es "Table ... already exists"
            msg = str(e).lower()
            if "already exists" in msg:
                logger.debug("Schema already exists (verified)")
            else:
                logger.critical(f"FATAL: Could not ensure Kuzu schema: {e}")
                raise RuntimeError(f"Kuzu Integrity Error: {e}")

    def create_memory_node(self, node: Any) -> str:
        """
        Persiste un MemoryNode4D en la base de datos de forma 100% segura.
        Usa consultas parametrizadas nativas si están disponibles, o serialización estricta en su defecto.
        """
        try:
            from cypher_codec import node_to_create_cypher
        except ImportError:
            from layers.l2_brain.cypher_codec import node_to_create_cypher

        # Intentamos consulta parametrizada primero
        try:
            if not self._execute_supports_parameters():
                raise NotImplementedError("IPC connection does not support parameters natively")
                
            if hasattr(node, "model_dump"):
                data = node.model_dump(mode="json")
            else:
                data = {k: v for k, v in node.__dict__.items() if not k.startswith("_")}

            cypher = (
                "CREATE (m:MemoryNode4D {"
                "causal_hash: $causal_hash, "
                "parent_hash: $parent_hash, "
                "locus_x: $locus_x, "
                "locus_y: $locus_y, "
                "locus_z: $locus_z, "
                "lamport_t: $lamport_t, "
                "authority_a: $authority_a, "
                "intent_i: $intent_i, "
                "payload: $payload, "
                "payload_hash: $payload_hash, "
                "embedding: $embedding})"
            )
            self.query(cypher, data)
            return node.causal_hash
        except Exception as e:
            logger.debug(f"Parameterized query not used ({e}). Executing strict serialization.")
            cypher_fallback = node_to_create_cypher(node)
            self.query(cypher_fallback)
            return node.causal_hash

    def _execute_supports_parameters(self) -> bool:
        import inspect
        try:
            # Si es proxy no soporta parámetros
            if self.conn.__class__.__name__.endswith("Proxy"):
                return False
            sig = inspect.signature(self.conn.execute)
            return len(sig.parameters) >= 2
        except Exception:
            return False

    def query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None):
        if not self.conn:
            logger.error("Attempted query on uninitialized KuzuRepository")
            raise ConnectionError("Kuzu connection not established")
        try:
            if parameters and self._execute_supports_parameters():
                return self.conn.execute(cypher, parameters)
            
            if parameters:
                # Fallback seguro si no soporta parámetros (ej. IPC bridge)
                try:
                    from cypher_codec import cypher_literal
                except ImportError:
                    from layers.l2_brain.cypher_codec import cypher_literal
                
                import re
                bound_cypher = cypher
                for key, val in parameters.items():
                    # Word boundaries evitan colisiones entre $id e $id_long
                    pattern = r'\$' + re.escape(key) + r'\b'
                    bound_cypher = re.sub(pattern, lambda m, v=val: cypher_literal(v), bound_cypher)
                return self.conn.execute(bound_cypher)
                
            return self.conn.execute(cypher)
        except Exception as e:
            logger.error(f"Kuzu Query Error: {e} | Cypher: {cypher} | Params: {parameters}")
            raise RuntimeError(f"Kuzu Execution Failure: {e}")

    def get_last_leaf_hash(self) -> str:
        res = self.query("MATCH (m:MemoryNode4D) RETURN m.causal_hash ORDER BY m.lamport_t DESC LIMIT 1")
        if res.has_next():
            return res.get_next()[0]
        return "GENESIS"

    def get_by_hash(self, causal_hash: str) -> Any:
        import re
        if causal_hash != "GENESIS" and not re.match(r"^[a-f0-9]{64}$", str(causal_hash)):
            logger.error(f"Security block: Invalid causal hash format: {causal_hash}")
            raise ValueError(f"Invalid causal hash format: {causal_hash}")

        try:
            from models import MemoryNode4D
        except ImportError:
            from layers.l2_brain.models import MemoryNode4D

        # Usamos nombres explícitos para desacoplar del orden físico de las columnas
        columns = [
            "causal_hash", "parent_hash", "locus_x", "locus_y", "locus_z",
            "lamport_t", "authority_a", "intent_i", "payload", "payload_hash", "embedding"
        ]
        return_clause = ", ".join([f"m.{c}" for c in columns])
        
        res = self.query(
            f"MATCH (m:MemoryNode4D) WHERE m.causal_hash = $causal_hash RETURN {return_clause}",
            {"causal_hash": causal_hash}
        )
        if res.has_next():
            row = res.get_next()
            return MemoryNode4D(
                causal_hash=row[0],
                parent_hash=row[1],
                locus_x=row[2],
                locus_y=row[3],
                locus_z=row[4],
                lamport_t=row[5],
                authority_a=row[6],
                intent_i=row[7],
                payload=row[8],
                payload_hash=row[9],
                embedding=row[10]
            )
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

    def find_similar_nodes(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Busca nodos semánticamente similares con fallback antifrágil.
        Si el motor Kùzu no soporta dot_product nativo, recuperamos candidatos y rankeamos en Python.
        """
        try:
            from embedding_provider import EmbeddingProvider
        except ImportError:
            from layers.l2_brain.embedding_provider import EmbeddingProvider
            
        query_vec = EmbeddingProvider.generate_vector(query_text)
        
        # [ANTI-FRAGILITY] Intentamos dot_product nativo primero
        try:
            cypher = (
                "MATCH (m:MemoryNode4D) "
                "RETURN m.causal_hash, m.payload, m.intent_i, "
                "CAST(dot_product(m.embedding, $query_vec) AS FLOAT) as score "
                "ORDER BY score DESC LIMIT $limit"
            )
            results = self.query(cypher, {"query_vec": query_vec, "limit": limit})
            matches = []
            while results.has_next():
                row = results.get_next()
                matches.append({"hash": row[0], "payload": row[1], "intent": row[2], "score": row[3]})
            return matches
        except Exception as e:
            logger.warning(f"Native dot_product failed ({e}). Falling back to client-side ranking.")
            # FALLBACK: Recuperar los últimos 100 nodos y rankear en memoria (Escalable para DUMMIE)
            cypher = "MATCH (m:MemoryNode4D) RETURN m.causal_hash, m.payload, m.intent_i, m.embedding ORDER BY m.lamport_t DESC LIMIT 100"
            results = self.query(cypher)
            matches = []
            while results.has_next():
                row = results.get_next()
                # [ROBUSTNESS] Asegurar que el embedding sea una lista de floats
                emb = row[3]
                if isinstance(emb, str):
                    try:
                        emb = json.loads(emb)
                    except:
                        emb = None
                
                score = EmbeddingProvider.similarity(query_vec, emb) if emb else 0.0
                matches.append({"hash": row[0], "payload": row[1], "intent": row[2], "score": score})
            
            matches.sort(key=lambda x: x["score"], reverse=True)
            return matches[:limit]

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

class SocraticodeAdapter(CodeAnalysisPort):
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def analyze_symbols(self, path: str) -> List[Dict[str, Any]]:
        try:
            result = await self.proxy.call_tool("socraticode", "analyze_directory", {"path": path})
            return result.get("symbols", [])
        except Exception as e:
            logger.error(f"Error en SocraticodeAdapter: {e}")
            return []

class PhoenixAdapter(ObservabilityPort):
    def __init__(self, proxy_manager: Any):
        self.proxy = proxy_manager

    async def record_trace(self, session_id: str, action: str, status: str) -> None:
        try:
            await self.proxy.call_tool("phoenix", "upsert-prompt", {
                "name": f"session_{session_id}",
                "template": f"Action: {action} | Status: {status}"
            })
        except Exception as e:
            logger.error(f"Error en PhoenixAdapter: {e}")

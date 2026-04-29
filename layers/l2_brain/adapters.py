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
            try:
                from models import MemoryNode4D
            except ImportError:
                from layers.l2_brain.models import MemoryNode4D
            
            # Ejecutar todas las consultas de esquema
            queries = []
            if hasattr(MemoryNode4D, "schema_creation_queries"):
                queries = MemoryNode4D.schema_creation_queries()
            else:
                queries = [MemoryNode4D.schema_creation_query()]
                
            for q in queries:
                try:
                    self.conn.execute(q)
                    logger.info(f"Executed schema query: {q[:30]}...")
                except Exception as e:
                    msg = str(e).lower()
                    if "already exists" in msg:
                        logger.debug(f"Schema element already exists: {q[:30]}")
                    else:
                        logger.critical(f"FATAL: Could not ensure Kuzu schema element: {e}")
                        raise RuntimeError(f"Kuzu Integrity Error: {e}")
        except RuntimeError:
            raise
        except Exception as e:
            logger.critical(f"FATAL: Unexpected error ensuring Kuzu schema: {e}")
            raise RuntimeError(f"Kuzu Integrity Error: {e}")

    def create_memory_node(self, node: Any) -> str:
        """
        Persiste un MemoryNode4D en la base de datos de forma 100% segura.
        Usa consultas parametrizadas nativas si están disponibles, o serialización estricta en su defecto.
        """
        # Idempotencia: Prevenir duplicados en reintentos
        try:
            existing = self.get_by_hash(node.causal_hash)
            if existing:
                logger.debug(f"MemoryNode4D {node.causal_hash} already persisted (idempotency ACK).")
                return node.causal_hash
        except ValueError:
            logger.error(f"Security block: Invalid causal hash format for idempotency: {node.causal_hash}")
            raise
        except Exception as e:
            logger.debug(f"Node lookup for idempotency returned no results (expected if new): {e}")

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
                "parent_hashes: $parent_hashes, "
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
        except Exception as e:
            logger.debug(f"Parameterized query not used ({e}). Executing strict serialization.")
            cypher_fallback = node_to_create_cypher(node)
            self.query(cypher_fallback)

        # [4D-TES Edge Creation]
        parents = getattr(node, "parent_hashes", [])
        if isinstance(parents, str):
            parents = [parents]
        elif not isinstance(parents, list):
            parents = []
            
        for p_hash in parents:
            if p_hash == "GENESIS":
                continue
            try:
                cypher_rel = (
                    "MATCH (p:MemoryNode4D), (c:MemoryNode4D) "
                    "WHERE p.causal_hash = $p_hash AND c.causal_hash = $c_hash "
                    "CREATE (p)-[:CAUSAL_LINK]->(c)"
                )
                self.query(cypher_rel, {"p_hash": p_hash, "c_hash": node.causal_hash})
                logger.info(f"Created CAUSAL_LINK from {p_hash} to {node.causal_hash}")
            except Exception as e:
                logger.warning(f"Could not create CAUSAL_LINK from {p_hash} to {node.causal_hash}: {e}")

        # [Paso B] Enriquecimiento vectorial asíncrono
        self._enqueue_vector_enrichment(node.causal_hash, node.payload)

        return node.causal_hash

    def _enqueue_vector_enrichment(self, causal_hash: str, payload: str):
        """
        [Paso B] Cola asíncrona de enriquecimiento vectorial.
        Dispara un hilo de fondo para actualizar los embeddings sin bloquear el flujo causal.
        """
        import threading

        def _enrich():
            try:
                try:
                    from embedding_provider import EmbeddingProvider
                except ImportError:
                    from layers.l2_brain.embedding_provider import EmbeddingProvider

                vec = EmbeddingProvider.generate_vector(payload)
                if vec and vec != [0.0]:
                    cypher_update = "MATCH (m:MemoryNode4D) WHERE m.causal_hash = $c_hash SET m.embedding = $embedding"
                    self.query(cypher_update, {"c_hash": causal_hash, "embedding": vec})
                    logger.info(f"Vector enrichment successful for node {causal_hash}")
            except Exception as e:
                logger.warning(f"Vector enrichment failed for node {causal_hash}: {e}")

        threading.Thread(target=_enrich, daemon=True).start()


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
            import hashlib
            cypher_hash = hashlib.sha256(cypher.encode()).hexdigest()[:12]
            param_keys = list(parameters.keys()) if parameters else []
            logger.error(f"Kuzu Query Error: {e} | CypherHash: {cypher_hash} | ParamKeys: {param_keys}")
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
            "causal_hash", "parent_hashes", "locus_x", "locus_y", "locus_z",
            "lamport_t", "authority_a", "intent_i", "payload", "payload_hash", "embedding"
        ]
        return_clause = ", ".join([f"m.{c}" for c in columns])
        
        res = self.query(
            f"MATCH (m:MemoryNode4D) WHERE m.causal_hash = $causal_hash RETURN {return_clause}",
            {"causal_hash": causal_hash}
        )
        if res.has_next():
            row = res.get_next()
            node = MemoryNode4D(
                causal_hash=row[0],
                parent_hashes=row[1] if isinstance(row[1], list) else [],
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
            try:
                from models import CausalIntegrityVerifier
            except ImportError:
                from layers.l2_brain.models import CausalIntegrityVerifier
                
            if not CausalIntegrityVerifier.verify_node(node):
                logger.critical(f"Causal Integrity Failure for node {causal_hash}")
                raise ValueError(f"Causal Integrity Failure: Node {causal_hash} has been tampered with.")
            return node
        return None

    def get_causal_chain(self, leaf_hash: str) -> List[Any]:
        visited = set()
        chain = []
        queue = [leaf_hash]
        while queue:
            current = queue.pop(0)
            if current == "GENESIS" or current in visited:
                continue
            node = self.get_by_hash(current)
            if node:
                visited.add(current)
                chain.append(node)
                for phash in getattr(node, "parent_hashes", []):
                    if phash != "GENESIS" and phash not in visited:
                        queue.append(phash)
        # Compatibilidad legacy: devolver leaf-first para facilitar replay causal.
        chain.sort(key=lambda n: n.lamport_t, reverse=True)
        return chain

    def find_similar_nodes(
        self,
        query_text: str,
        limit: int = 5,
        include_proof_subgraph: bool = False,
        tau_threshold: float = 0.8,
    ) -> List[Dict[str, Any]]:
        """
        Busca nodos semánticamente similares integrando el Score Epistémico y Ranking Causal.
        """
        try:
            from embedding_provider import EmbeddingProvider
            from domain.retrieval_service import RetrievalService
        except ImportError:
            from layers.l2_brain.embedding_provider import EmbeddingProvider
            from layers.l2_brain.domain.retrieval_service import RetrievalService
            
        try:
            from models import MemoryNode4D
        except ImportError:
            from layers.l2_brain.models import MemoryNode4D

        query_vec = EmbeddingProvider.generate_vector(query_text)
        
        columns = [
            "causal_hash", "parent_hashes", "locus_x", "locus_y", "locus_z",
            "lamport_t", "authority_a", "intent_i", "payload", "payload_hash", "embedding"
        ]
        return_clause = ", ".join([f"m.{c}" for c in columns])
        
        # Traer un pool de 100 candidatos recientes
        res = self.query(f"MATCH (m:MemoryNode4D) RETURN {return_clause} ORDER BY m.lamport_t DESC LIMIT 100")
        
        nodes = []
        similarities = []
        
        while res.has_next():
            row = res.get_next()
            node = MemoryNode4D(
                causal_hash=row[0],
                parent_hashes=row[1] if isinstance(row[1], list) else [],
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
            nodes.append(node)
            sim = EmbeddingProvider.similarity(query_vec, node.embedding) if node.embedding else 0.0
            similarities.append(sim)
            
        # Rankeo Epistémico
        ranked = RetrievalService.rank_nodes(nodes, similarities)
        
        matches = []
        for node in ranked[:limit]:
            idx = nodes.index(node)
            score = similarities[idx]
            match = {
                "hash": node.causal_hash, 
                "payload": node.payload, 
                "intent": node.intent_i, 
                "score": score
            }
            if include_proof_subgraph:
                proof_nodes = RetrievalService.extract_minimal_proof_subgraph(
                    node,
                    self.get_by_hash,
                    query_sim=score,
                    tau_threshold=tau_threshold,
                )
                match["proof_subgraph"] = [proof_node.causal_hash for proof_node in proof_nodes]
                match["proof_size"] = len(proof_nodes)
            matches.append(match)
            
        return matches

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

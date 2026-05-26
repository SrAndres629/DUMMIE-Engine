import os
import base64
import logging
import glob
import numpy as np
from typing import Dict, Any, List, Optional

try:
    import zstd
except ImportError:
    zstd = None

logger = logging.getLogger("brain.adapters.kuzu")


class KuzuRepository:
    def __init__(self, db_path: Optional[str] = None, db: Any = None):
        self.db = db
        self.read_only = False
        self.conn = None
        if db:
            logger.info(f"KuzuRepository: Initializing with existing DB object: {db}")
            if hasattr(db, "ipc"):
                # [SPEC-30] Memory Plane (Arrow IPC)
                self.conn = db.ipc
                logger.info("KuzuRepository initialized in IPC mode (Zero-Copy)")
            else:
                # Modo Nativo
                import kuzu

                self.conn = kuzu.Connection(db)
                logger.info(f"KuzuRepository: Native connection created: {self.conn}")
        elif db_path:
            import kuzu
            import glob

            if os.path.isdir(db_path):
                raise ValueError("Kuzu database path cannot be a directory")
            elif os.path.isfile(db_path):
                pass

            parent_dir = os.path.dirname(os.path.abspath(db_path))
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
                logger.info(f"Created parent directory for Kuzu: {parent_dir}")

            try:
                self.db = kuzu.Database(db_path)
            except Exception as e:
                logger.warning(
                    f"Database init failed ({e}). Attempting lock recovery for {db_path}..."
                )
                if os.path.isdir(db_path):
                    for lock_file in glob.glob(os.path.join(db_path, "*.lock")):
                        try:
                            os.remove(lock_file)
                            logger.info(f"Removed orphan lock file: {lock_file}")
                        except OSError:
                            pass
                self.db = kuzu.Database(db_path)

            self.conn = kuzu.Connection(self.db)
            logger.warning(
                "[!] ALERTA DE SOBERANÍA: KuzuRepository ha inicializado en Modo NATIVO (Lock físico)."
            )
            self._ensure_schema()

    def _ensure_schema(self):
        """Crea las tablas necesarias si no existen con el esquema SOVEREIGN-4D."""
        if not self.conn:
            return
        try:
            try:
                from layers.l2_brain.l2_memory_models import MemoryNode4D
            except ImportError:
                from layers.l2_brain.l2_memory_models import MemoryNode4D

            # [IDEMPOTENCY] Execute all schema queries
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
                    if "already exists" in str(e).lower():
                        logger.debug(f"Schema element already exists: {q[:30]}")
                    else:
                        logger.critical(
                            f"FATAL: Could not ensure Kuzu schema element: {e}"
                        )
                        raise RuntimeError(f"Kuzu Integrity Error: {e}")
        except Exception as e:
            if not isinstance(e, RuntimeError):
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
                logger.debug(
                    f"MemoryNode4D {node.causal_hash} already persisted (idempotency ACK)."
                )
                return node.causal_hash
        except ValueError:
            logger.error(
                f"Security block: Invalid causal hash format for idempotency: {node.causal_hash}"
            )
            raise
        except Exception as e:
            logger.debug(
                f"Node lookup for idempotency returned no results (expected if new): {e}"
            )

        try:
            from cypher_codec import node_to_create_cypher
        except ImportError:
            from layers.l2_brain.cypher_codec import node_to_create_cypher

        # Intentamos consulta parametrizada primero
        try:
            if not self._execute_supports_parameters():
                raise NotImplementedError(
                    "IPC connection does not support parameters natively"
                )

            if hasattr(node, "model_dump"):
                data = node.model_dump(mode="json")
            else:
                data = {k: v for k, v in node.__dict__.items() if not k.startswith("_")}

            raw_payload = str(data.get("payload", ""))
            if zstd and len(raw_payload) > 1024:
                compressed = zstd.compress(raw_payload.encode("utf-8"))
                data["payload"] = base64.b64encode(compressed).decode("utf-8")

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
            logger.debug(
                f"Parameterized query not used ({e}). Executing strict serialization."
            )
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
                logger.warning(
                    f"Could not create CAUSAL_LINK from {p_hash} to {node.causal_hash}: {e}"
                )

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

                pattern = r"\$([A-Za-z0-9_]+)\b"

                def replace_placeholder(m):
                    k = m.group(1)
                    if k in parameters:
                        return cypher_literal(parameters[k])
                    return m.group(0)

                bound_cypher = re.sub(pattern, replace_placeholder, cypher)
                return self.conn.execute(bound_cypher)

            return self.conn.execute(cypher)
        except Exception as e:
            import hashlib

            cypher_hash = hashlib.sha256(cypher.encode()).hexdigest()[:12]
            param_keys = list(parameters.keys()) if parameters else []
            logger.error(
                f"Kuzu Query Error: {e} | CypherHash: {cypher_hash} | ParamKeys: {param_keys}"
            )
            raise RuntimeError(f"Kuzu Execution Failure: {e}")

    def get_last_leaf_hash(self) -> str:
        res = self.query(
            "MATCH (m:MemoryNode4D) RETURN m.causal_hash ORDER BY m.lamport_t DESC LIMIT 1"
        )
        if res.has_next():
            return res.get_next()[0]
        return "GENESIS"

    def get_by_hash(self, causal_hash: str) -> Any:
        import re

        if causal_hash != "GENESIS" and not re.match(
            r"^[a-f0-9]{64}$", str(causal_hash)
        ):
            logger.error(f"Security block: Invalid causal hash format: {causal_hash}")
            raise ValueError(f"Invalid causal hash format: {causal_hash}")

        try:
            from layers.l2_brain.l2_memory_models import MemoryNode4D
        except ImportError:
            from layers.l2_brain.l2_memory_models import MemoryNode4D

        # Usamos nombres explícitos para desacoplar del orden físico de las columnas
        columns = [
            "causal_hash",
            "parent_hashes",
            "locus_x",
            "locus_y",
            "locus_z",
            "lamport_t",
            "authority_a",
            "intent_i",
            "payload",
            "payload_hash",
            "embedding",
        ]
        return_clause = ", ".join([f"m.{c}" for c in columns])

        res = self.query(
            f"MATCH (m:MemoryNode4D) WHERE m.causal_hash = $causal_hash RETURN {return_clause}",
            {"causal_hash": causal_hash},
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
                payload=self._try_decompress(row[8]),
                payload_hash=row[9],
                embedding=row[10],
            )
            try:
                from layers.l2_brain.l2_memory_models import CausalIntegrityVerifier
            except ImportError:
                from layers.l2_brain.l2_memory_models import CausalIntegrityVerifier

            if not CausalIntegrityVerifier.verify_node(node):
                logger.critical(f"Causal Integrity Failure for node {causal_hash}")
                raise ValueError(
                    f"Causal Integrity Failure: Node {causal_hash} has been tampered with."
                )
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
            from layers.l2_brain.model_mesh.embedding_provider import EmbeddingProvider
            from domain.retrieval_service import RetrievalService
        except ImportError:
            from layers.l2_brain.embedding_provider import EmbeddingProvider
            from layers.l2_brain.domain.retrieval_service import RetrievalService

        try:
            from layers.l2_brain.l2_memory_models import MemoryNode4D
        except ImportError:
            from layers.l2_brain.l2_memory_models import MemoryNode4D

        query_vec = EmbeddingProvider.generate_vector(query_text)

        columns = [
            "causal_hash",
            "parent_hashes",
            "locus_x",
            "locus_y",
            "locus_z",
            "lamport_t",
            "authority_a",
            "intent_i",
            "payload",
            "payload_hash",
            "embedding",
        ]
        return_clause = ", ".join([f"m.{c}" for c in columns])

        # Traer un pool de 100 candidatos recientes
        res = self.query(
            f"MATCH (m:MemoryNode4D) RETURN {return_clause} ORDER BY m.lamport_t DESC LIMIT 100"
        )

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
                payload=self._try_decompress(row[8]),
                payload_hash=row[9],
                embedding=row[10],
            )
            nodes.append(node)
            sim = (
                EmbeddingProvider.similarity(query_vec, node.embedding)
                if node.embedding
                else 0.0
            )
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
                "score": score,
            }
            if include_proof_subgraph:
                proof_nodes = RetrievalService.extract_minimal_proof_subgraph(
                    node,
                    self.get_by_hash,
                    query_sim=score,
                    tau_threshold=tau_threshold,
                )
                match["proof_subgraph"] = [
                    proof_node.causal_hash for proof_node in proof_nodes
                ]
                match["proof_size"] = len(proof_nodes)
            matches.append(match)

        return matches

    def semantic_search(self, query_vector: List[float], top_k: int = 5) -> List[Any]:
        try:
            from layers.l2_brain.model_mesh.embedding_provider import EmbeddingProvider
        except ImportError:
            from layers.l2_brain.embedding_provider import EmbeddingProvider

        try:
            from layers.l2_brain.l2_memory_models import MemoryNode4D
        except ImportError:
            from layers.l2_brain.l2_memory_models import MemoryNode4D

        columns = [
            "causal_hash",
            "parent_hashes",
            "locus_x",
            "locus_y",
            "locus_z",
            "lamport_t",
            "authority_a",
            "intent_i",
            "payload",
            "payload_hash",
            "embedding",
        ]
        return_clause = ", ".join([f"m.{c}" for c in columns])

        result = self.query(
            f"MATCH (m:MemoryNode4D) WHERE m.embedding IS NOT NULL "
            f"RETURN {return_clause} ORDER BY m.lamport_t DESC LIMIT 100"
        )

        nodes = []
        similarities = []
        while result.has_next():
            row = result.get_next()
            node = MemoryNode4D(
                causal_hash=row[0],
                parent_hashes=row[1] if isinstance(row[1], list) else [],
                locus_x=row[2],
                locus_y=row[3],
                locus_z=row[4],
                lamport_t=row[5],
                authority_a=row[6],
                intent_i=row[7],
                payload=self._try_decompress(row[8]),
                payload_hash=row[9],
                embedding=row[10],
            )
            nodes.append(node)
            sim = (
                EmbeddingProvider.similarity(query_vector, node.embedding)
                if node.embedding
                else 0.0
            )
            similarities.append(sim)

        ranked = sorted(
            range(len(similarities)), key=lambda i: similarities[i], reverse=True
        )
        return [nodes[i] for i in ranked[:top_k]]

    def hybrid_search(
        self,
        query_vector: List[float],
        locus_x: Optional[str] = None,
        intent_i: Optional[List[str]] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        where_clauses = ["m.embedding IS NOT NULL"]
        params = {}

        if locus_x:
            where_clauses.append("m.locus_x = $lx")
            params["lx"] = locus_x

        if intent_i:
            where_clauses.append("m.intent_i IN $ii")
            params["ii"] = intent_i

        where_stmt = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        columns = ["causal_hash", "embedding", "lamport_t", "authority_a"]
        return_clause = ", ".join([f"m.{c}" for c in columns])

        query = f"MATCH (m:MemoryNode4D){where_stmt} RETURN {return_clause}"
        result = self.query(query, params)
        scored_results = []

        q_vec = np.array(query_vector)
        q_norm = np.linalg.norm(q_vec)

        while result.has_next():
            row = result.get_next()
            causal_hash = row[0]
            emb = row[1]
            lamport_t = int(row[2])
            authority = str(row[3])

            if not emb or len(emb) != len(query_vector):
                similarity = 0.0
            else:
                m_vec = np.array(emb)
                m_norm = np.linalg.norm(m_vec)
                if q_norm > 0 and m_norm > 0:
                    similarity = float(np.dot(q_vec, m_vec) / (q_norm * m_norm))
                else:
                    similarity = 0.0

            auth_score = {
                "OVERSEER": 1.0,
                "HUMAN": 0.95,
                "ENGINEER": 0.8,
                "AGENT": 0.7,
            }.get(authority, 0.5)
            recency_score = min(1.0, lamport_t / 1000.0) if lamport_t > 0 else 0.0

            final_score = (
                (0.7 * similarity) + (0.2 * auth_score) + (0.1 * recency_score)
            )

            scored_results.append(
                {
                    "causal_hash": causal_hash,
                    "score": round(final_score, 4),
                    "similarity": round(similarity, 4),
                }
            )

        scored_results.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = scored_results[:top_k]

        final_nodes = []
        for cand in top_candidates:
            node = self.get_by_hash(cand["causal_hash"])
            if node:
                final_nodes.append(
                    {
                        "node": node,
                        "score": cand["score"],
                        "similarity": cand["similarity"],
                    }
                )

        return final_nodes

    def compute_blast_radius(self, causal_hash: str) -> dict:
        query = (
            "MATCH (root:MemoryNode4D {causal_hash: $ch})<-[:CAUSAL_LINK*]-"
            "(dependent:MemoryNode4D) "
            "RETURN dependent.locus_x, dependent.locus_y, COUNT(*)"
        )
        result = self.query(query, {"ch": causal_hash})

        impacted_loci = []
        total_nodes = 0
        while result.has_next():
            row = result.get_next()
            count = row[2]
            total_nodes += count
            impacted_loci.append(
                {
                    "locus_x": row[0],
                    "locus_y": row[1],
                    "nodes_count": count,
                }
            )

        return {
            "root_hash": causal_hash,
            "impact_level": "HIGH" if total_nodes > 5 else "LOW",
            "impacted_loci": impacted_loci,
            "total_impacted_nodes": total_nodes,
        }

    def get_max_lamport_tick(self) -> int:
        try:
            result = self.query("MATCH (m:MemoryNode4D) RETURN max(m.lamport_t)")
            if result.has_next():
                row = result.get_next()
                max_tick = row[0]
                if max_tick is not None:
                    return int(max_tick)
        except Exception:
            pass
        return 0

    def _try_decompress(self, raw_payload: str) -> str:
        if zstd is None:
            return raw_payload
        try:
            compressed = base64.b64decode(raw_payload)
            return zstd.decompress(compressed).decode("utf-8")
        except Exception:
            return raw_payload

    def append(self, node: Any) -> str:
        return self.create_memory_node(node)


class KuzuSkillRepository(KuzuRepository):
    def __init__(self, db_path=None, db=None):
        super().__init__(db_path=db_path, db=db)
        if not self.read_only:
            try:
                self.conn.execute(
                    "CREATE NODE TABLE Skill("
                    "skill_id STRING, "
                    "yaml_payload STRING, "
                    "source_causal_hashes STRING, "
                    "skill_hash STRING, "
                    "PRIMARY KEY (skill_id))"
                )
            except Exception:
                pass

    def save_skill(self, skill: Any) -> None:
        if self.read_only:
            raise RuntimeError("KuzuDB is read-only; cannot save skill")
        import json

        payload = (
            json.dumps(skill.source_causal_hashes)
            if hasattr(skill, "source_causal_hashes")
            else "[]"
        )
        self.conn.execute(
            "MERGE (s:Skill {skill_id: $sid}) "
            "SET s.yaml_payload = $yaml, "
            "s.source_causal_hashes = $sources, "
            "s.skill_hash = $hash",
            {
                "sid": skill.skill_id,
                "yaml": skill.yaml_payload,
                "sources": payload,
                "hash": skill.skill_hash,
            },
        )

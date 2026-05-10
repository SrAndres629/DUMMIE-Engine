import os
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger("brain.adapters.kuzu")

class KuzuRepository:
    def __init__(self, db_path: Optional[str] = None, db: Any = None):
        self.db = db
        self.read_only = False
        self.conn = None
        if db:
            if hasattr(db, "ipc"):
                self.conn = db.ipc
                logger.info("KuzuRepository initialized in IPC mode")
            else:
                import kuzu
                self.conn = kuzu.Connection(db)
        elif db_path:
            import kuzu
            if os.path.isdir(db_path):
                if not os.listdir(db_path):
                    logger.error(f"CRITICAL: Kuzu path '{db_path}' is an empty directory.")
                    raise ValueError(f"Invalid Kuzu database path: '{db_path}' is a directory.")
            
            parent_dir = os.path.dirname(os.path.abspath(db_path))
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir, exist_ok=True)
            
            self.db = kuzu.Database(db_path)
            self.conn = kuzu.Connection(self.db)
            self._ensure_schema()

    def _ensure_schema(self):
        if not self.conn: return
        try:
            try:
                from models import MemoryNode4D
            except ImportError:
                from layers.l2_brain.models import MemoryNode4D
            self.conn.execute(MemoryNode4D.schema_creation_query())
        except Exception as e:
            if "already exists" not in str(e).lower():
                raise RuntimeError(f"Kuzu Integrity Error: {e}")

    def create_memory_node(self, node: Any) -> str:
        try:
            from cypher_codec import node_to_create_cypher
        except ImportError:
            from layers.l2_brain.cypher_codec import node_to_create_cypher

        cypher_fallback = node_to_create_cypher(node)
        self.query(cypher_fallback)
        return node.causal_hash

    def query(self, cypher: str, parameters: Optional[Dict[str, Any]] = None):
        if not self.conn:
            raise ConnectionError("Kuzu connection not established")
        try:
            if parameters:
                try:
                    from cypher_codec import cypher_literal
                except ImportError:
                    from layers.l2_brain.cypher_codec import cypher_literal
                import re
                bound_cypher = cypher
                for key, val in parameters.items():
                    pattern = r'\$' + re.escape(key) + r'\b'
                    bound_cypher = re.sub(pattern, lambda m, v=val: cypher_literal(v), bound_cypher)
                return self.conn.execute(bound_cypher)
            return self.conn.execute(cypher)
        except Exception as e:
            raise RuntimeError(f"Kuzu Execution Failure: {e}")

    def get_last_leaf_hash(self) -> str:
        res = self.query("MATCH (m:MemoryNode4D) RETURN m.causal_hash ORDER BY m.lamport_t DESC LIMIT 1")
        if res.has_next():
            return res.get_next()[0]
        return "GENESIS"

    def get_by_hash(self, causal_hash: str) -> Any:
        try:
            from models import MemoryNode4D, CausalIntegrityVerifier
        except ImportError:
            from layers.l2_brain.models import MemoryNode4D, CausalIntegrityVerifier

        if causal_hash != "GENESIS":
            import re
            if not re.match(r"^[a-f0-9]{64}$", str(causal_hash)):
                raise ValueError(f"Invalid causal hash format: {causal_hash}")

        columns = ["causal_hash", "parent_hashes", "locus_x", "locus_y", "locus_z", "lamport_t", "authority_a", "intent_i", "payload", "payload_hash", "embedding"]
        return_clause = ", ".join([f"m.{c}" for c in columns])
        
        res = self.query(f"MATCH (m:MemoryNode4D) WHERE m.causal_hash = $causal_hash RETURN {return_clause}", {"causal_hash": causal_hash})
        if res.has_next():
            row = res.get_next()
            node = MemoryNode4D(
                causal_hash=row[0],
                parent_hashes=row[1] if isinstance(row[1], list) else [],
                locus_x=row[2], locus_y=row[3], locus_z=row[4],
                lamport_t=row[5], authority_a=row[6], intent_i=row[7],
                payload=row[8], payload_hash=row[9], embedding=row[10]
            )
            if not CausalIntegrityVerifier.verify_node(node):
                raise ValueError(f"Causal Integrity Failure for node {causal_hash}")
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
        chain.sort(key=lambda n: n.lamport_t, reverse=True)
        return chain

    def find_similar_nodes(self, query_text: str, limit: int = 5, include_proof_subgraph: bool = False, tau_threshold: float = 0.8) -> List[Dict[str, Any]]:
        try:
            from embedding_provider import EmbeddingProvider
            from domain.retrieval_service import RetrievalService
            from models import MemoryNode4D
        except ImportError:
            from layers.l2_brain.embedding_provider import EmbeddingProvider
            from layers.l2_brain.domain.retrieval_service import RetrievalService
            from layers.l2_brain.models import MemoryNode4D

        query_vec = EmbeddingProvider.generate_vector(query_text)
        columns = ["causal_hash", "parent_hashes", "locus_x", "locus_y", "locus_z", "lamport_t", "authority_a", "intent_i", "payload", "payload_hash", "embedding"]
        return_clause = ", ".join([f"m.{c}" for c in columns])
        
        res = self.query(f"MATCH (m:MemoryNode4D) RETURN {return_clause} ORDER BY m.lamport_t DESC LIMIT 100")
        nodes, similarities = [], []
        
        while res.has_next():
            row = res.get_next()
            node = MemoryNode4D(
                causal_hash=row[0],
                parent_hashes=row[1] if isinstance(row[1], list) else [],
                locus_x=row[2], locus_y=row[3], locus_z=row[4],
                lamport_t=row[5], authority_a=row[6], intent_i=row[7],
                payload=row[8], payload_hash=row[9], embedding=row[10]
            )
            nodes.append(node)
            sim = EmbeddingProvider.similarity(query_vec, node.embedding) if node.embedding else 0.0
            similarities.append(sim)
            
        ranked = RetrievalService.rank_nodes(nodes, similarities)
        matches = []
        for node in ranked[:limit]:
            idx = nodes.index(node)
            match = {"hash": node.causal_hash, "payload": node.payload, "intent": node.intent_i, "score": similarities[idx]}
            if include_proof_subgraph:
                proof_nodes = RetrievalService.extract_minimal_proof_subgraph(node, self.get_by_hash, query_sim=similarities[idx], tau_threshold=tau_threshold)
                match["proof_subgraph"] = [pn.causal_hash for pn in proof_nodes]
                match["proof_size"] = len(proof_nodes)
            matches.append(match)
        return matches

class KuzuSkillRepository(KuzuRepository):
    pass

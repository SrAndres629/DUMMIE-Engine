import kuzu
import zstd
import os
import json
import hashlib
import base64
from typing import Optional, List, Dict, Any
import numpy as np
from brain.domain.memory.ports import (
    IEventStorePort,
    IStructuralAnalysisPort,
    ISkillRepositoryPort,
)
from brain.domain.memory.models import MemoryNode4DTES
from brain.domain.context.models import SixDimensionalContext


class KuzuRepository(IEventStorePort, IStructuralAnalysisPort):
    """
    Implementación del repositorio 4D-TES utilizando KùzuDB (Spec 02).
    Soporta persistencia Merkle-DAG y análisis estructural de grafos.
    Spec: DE-V2-L2-110
    """

    def __init__(self, db_path: str = ".aiwg/memory/kuzu_4d", db: kuzu.Database = None):
        self.db_path = db_path
        self.read_only = False

        if db is not None:
            self.db = db
        else:
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

            try:
                self.db = kuzu.Database(self.db_path)
            except RuntimeError as e:
                # Si el DB está bloqueado por otro proceso (p. ej. otro MCP/cliente),
                # arrancamos en modo read-only para que el servidor no "muera" en bootstrap.
                # Las operaciones de escritura deben fallar explícitamente.
                if "Could not set lock on file" in str(e):
                    self.db = kuzu.Database(self.db_path, read_only=True)
                    self.read_only = True
                else:
                    raise

        self.conn = kuzu.Connection(self.db)
        if not self.read_only:
            self._initialize_schema()

    def _initialize_schema(self):
        """Inicializa las tablas y relaciones si no existen (Spec 02/205)."""
        try:
            # 1. Intentar creación base
            self.conn.execute("""
                CREATE NODE TABLE MemoryNode4D(
                    causal_hash STRING,
                    parent_hashes STRING[],
                    locus_x STRING,
                    locus_y STRING,
                    locus_z STRING,
                    lamport_t INT64,
                    authority_a STRING,
                    intent_i STRING,
                    payload STRING,
                    payload_hash STRING,
                    embedding FLOAT[],
                    vector_space STRING,
                    PRIMARY KEY (causal_hash)
                )
            """)
        except Exception:
            # La tabla ya existe, intentar migraciones quirúrgicas
            try:
                # Kùzu no soporta ALTER TABLE ADD COLUMN todavía en todas las versiones de forma estable.
                # Si falla la creación, asumimos que ya está o que hay que manejarlo en el código.
                # Como medida preventiva, intentamos añadir las nuevas columnas si la versión lo permite.
                self.conn.execute("ALTER TABLE MemoryNode4D ADD parent_hashes STRING[]")
            except Exception: pass
            try:
                self.conn.execute("ALTER TABLE MemoryNode4D ADD vector_space STRING")
            except Exception: pass

        try:
            # Nodos de Dominio (Spec 02)
            self.conn.execute("CREATE NODE TABLE Agent(id STRING, name STRING, PRIMARY KEY (id))")
            self.conn.execute("CREATE NODE TABLE Requirement(id STRING, spec STRING, PRIMARY KEY (id))")
            
            # Relaciones Merkle-DAG (Spec 02)
            self.conn.execute("CREATE REL TABLE CAUSED_BY(FROM MemoryNode4D TO MemoryNode4D)")
            self.conn.execute("CREATE REL TABLE EXECUTED_BY(FROM MemoryNode4D TO Agent)")
            self.conn.execute("CREATE REL TABLE VALIDATES(FROM MemoryNode4D TO Requirement)")
        except Exception:
            pass

    def append(self, node: MemoryNode4DTES) -> bool:
        """Persiste un nodo 4D-TES en el grafo."""
        if self.read_only:
            raise RuntimeError(
                f"KùzuDB está en modo read-only (posible lock de otro proceso) para {self.db_path}"
            )
        # Asegurar que el payload son bytes para compresión (Spec 02)
        raw_payload = node.payload
        if isinstance(raw_payload, str):
            raw_payload = raw_payload.encode("utf-8")

        compressed_payload = zstd.compress(raw_payload)
        # Codificar en Base64 para persistencia como STRING (evita problemas de Binder con BLOB)
        b64_payload = base64.b64encode(compressed_payload).decode("utf-8")

        query = """
        CREATE (m:MemoryNode4D {
            causal_hash: $ch,
            parent_hashes: $phs,
            payload: $py,
            payload_hash: $pyh,
            locus_x: $lx,
            locus_y: $ly,
            locus_z: $lz,
            lamport_t: $lt,
            authority_a: $aa,
            intent_i: $ii,
            embedding: $emb,
            vector_space: $vs
        })
        """
        self.conn.execute(
            query,
            {
                "ch": node.causal_hash,
                "phs": node.parent_hashes,
                "py": b64_payload,
                "pyh": node.payload_hash,
                "lx": node.context.locus_x,
                "ly": node.context.locus_y,
                "lz": node.context.locus_z,
                "lt": node.context.lamport_t,
                "aa": node.context.authority_a.value
                if hasattr(node.context.authority_a, "value")
                else str(node.context.authority_a),
                "ii": node.context.intent_i.value
                if hasattr(node.context.intent_i, "value")
                else str(node.context.intent_i),
                "emb": node.embedding,
                "vs": getattr(node, "vector_space", "TEXT_FAST_BGE_SMALL_384"),
            },
        )

        # Crear arcos de causalidad (Spec 02)
        for ph in node.parent_hashes:
            if ph != "GENESIS":
                self.conn.execute(
                    "MATCH (p:MemoryNode4D {causal_hash: $ph}), (c:MemoryNode4D {causal_hash: $ch}) "
                    "CREATE (c)-[:CAUSED_BY]->(p)",
                    {"ph": ph, "ch": node.causal_hash},
                )
        return True

    def get_by_hash(self, causal_hash: str) -> Optional[MemoryNode4DTES]:
        """Recupera un nodo por su hash causal."""
        result = self.conn.execute(
            "MATCH (m:MemoryNode4D {causal_hash: $ch}) RETURN m.*", {"ch": causal_hash}
        )
        if result.has_next():
            row = result.get_next()
            # Decompress and decode Base64
            b64_payload = row[8]
            compressed = base64.b64decode(b64_payload)
            payload = zstd.decompress(compressed)

            payload = payload.decode("utf-8")

            return MemoryNode4DTES(
                causal_hash=row[0],
                parent_hashes=row[1] if row[1] else ["GENESIS"],
                locus_x=row[2],
                locus_y=row[3],
                locus_z=row[4],
                lamport_t=row[5],
                authority_a=row[6],
                intent_i=row[7],
                payload=payload,
                payload_hash=row[9],
                embedding=row[10],
                vector_space=row[11] if len(row) > 11 else "TEXT_FAST_BGE_SMALL_384",
            )
        return None

    def get_last_leaf_hash(self, locus_x: Optional[str] = None) -> str:
        """Retorna el hash del último nodo (u hoja) del DAG."""
        query = "MATCH (m:MemoryNode4D) "
        if locus_x:
            query += "WHERE m.locus_x = $lx "
        query += "RETURN m.causal_hash ORDER BY m.lamport_t DESC LIMIT 1"

        result = self.conn.execute(query, {"lx": locus_x} if locus_x else {})
        if result.has_next():
            return result.get_next()[0]
        return "GENESIS"

    def get_max_lamport_tick(self) -> int:
        """Recupera el tick máximo del 4D-TES para garantizar monotonía causal (Spec 02)."""
        try:
            result = self.conn.execute("MATCH (m:MemoryNode4D) RETURN max(m.lamport_t)")
            if result.has_next():
                row = result.get_next()
                max_tick = row[0]
                if max_tick is not None:
                    return int(max_tick)
        except Exception:
            pass
        return 0

    def get_causal_chain(
        self, leaf_hash: str, depth: int = 30
    ) -> List[MemoryNode4DTES]:
        """Reconstruye la cadena de causalidad (Merkle-DAG) desde una hoja hasta la raíz."""
        chain = []
        current_hashes = [leaf_hash]
        visited = set()
        
        while current_hashes and len(chain) < depth:
            next_hashes = []
            for h in current_hashes:
                if h == "GENESIS" or h in visited:
                    continue
                node = self.get_by_hash(h)
                if node:
                    chain.append(node)
                    visited.add(h)
                    next_hashes.extend(node.parent_hashes)
            current_hashes = next_hashes
            
        return chain

    def semantic_search(
        self, query_vector: List[float], top_k: int = 5
    ) -> List[MemoryNode4DTES]:
        """
        Búsqueda semántica usando distancia coseno sobre KùzuDB (Spec Local-RAG).
        """
        # Kùzu 0.11+ admite cosine_similarity
        query = """
        MATCH (m:MemoryNode4D)
        WHERE m.embedding IS NOT NULL
        RETURN m.causal_hash, cosine_similarity(m.embedding, $vec) as similarity
        ORDER BY similarity DESC
        LIMIT $k
        """
        result = self.conn.execute(query, {"vec": query_vector, "k": top_k})
        nodes = []
        while result.has_next():
            row = result.get_next()
            node = self.get_by_hash(row[0])
            if node:
                nodes.append(node)
        return nodes

    def hybrid_search(
        self,
        query_vector: List[float],
        locus_x: Optional[str] = None,
        intent_i: Optional[List[str]] = None,
        top_k: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda híbrida (Semántica + 6D Filters + Scoring Causal).
        Retorna nodos con sus scores calculados.
        """
        where_clauses = ["m.embedding IS NOT NULL"]
        params = {}

        if locus_x:
            where_clauses.append("m.locus_x = $lx")
            params["lx"] = locus_x

        if intent_i:
            where_clauses.append("m.intent_i IN $ii")
            params["ii"] = intent_i

        where_stmt = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        # Fetch candidates with embedding for Python-side scoring
        query = f"""
        MATCH (m:MemoryNode4D)
        {where_stmt}
        RETURN m.causal_hash, m.embedding, m.lamport_t, m.authority_a
        """
        
        result = self.conn.execute(query, params)
        scored_results = []
        
        # Pre-convert query vector to numpy for efficiency
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
                # Python-side cosine similarity
                m_vec = np.array(emb)
                m_norm = np.linalg.norm(m_vec)
                if q_norm > 0 and m_norm > 0:
                    similarity = float(np.dot(q_vec, m_vec) / (q_norm * m_norm))
                else:
                    similarity = 0.0
            
            # Simple scoring logic for hybrid ranking
            auth_score = {"OVERSEER": 1.0, "HUMAN": 0.95, "AGENT": 0.7}.get(authority, 0.5)
            recency_score = min(1.0, lamport_t / 1000.0) if lamport_t > 0 else 0.0
            
            final_score = (0.7 * similarity) + (0.2 * auth_score) + (0.1 * recency_score)
            
            # We only keep the top_k * 2 candidates for the final fetch to avoid overhead
            scored_results.append({
                "causal_hash": causal_hash,
                "score": round(final_score, 4),
                "similarity": round(similarity, 4)
            })
        
        scored_results.sort(key=lambda x: x["score"], reverse=True)
        top_candidates = scored_results[:top_k]
        
        final_nodes = []
        for cand in top_candidates:
            node = self.get_by_hash(cand["causal_hash"])
            if node:
                final_nodes.append({
                    "node": node,
                    "score": cand["score"],
                    "similarity": cand["similarity"]
                })
        
        return final_nodes

    def compute_blast_radius(self, causal_hash: str) -> dict:
        """
        Analiza el radio de impacto de un cambio (Spec 31).
        Utiliza consultas recursivas en el grafo para identificar nodos dependientes.
        """
        # Buscar todos los nodos que descienden de este (tienen este hash como ancestro)
        query = """
        MATCH (root:MemoryNode4D {causal_hash: $ch})<-[:CAUSED_BY*]-(dependent:MemoryNode4D)
        RETURN dependent.locus_x, dependent.locus_y, COUNT(*)
        """
        result = self.conn.execute(query, {"ch": causal_hash})

        impacted_loci = []
        total_nodes = 0
        while result.has_next():
            row = result.get_next()
            count = row[2]
            total_nodes += count
            impacted_loci.append(
                {"locus_x": row[0], "locus_y": row[1], "nodes_count": count}
            )

        return {
            "root_hash": causal_hash,
            "impact_level": "HIGH" if total_nodes > 5 else "LOW",
            "impacted_loci": impacted_loci,
            "total_impacted_nodes": total_nodes,
        }


class KuzuSkillRepository(ISkillRepositoryPort):
    """Repositorio de skills cristalizadas respaldado por Kùzu."""

    def __init__(self, repo: KuzuRepository):
        self.repo = repo
        if not self.repo.read_only:
            try:
                self.repo.conn.execute(
                    """
                    CREATE NODE TABLE Skill(
                        skill_id STRING,
                        yaml_payload STRING,
                        source_causal_hashes STRING,
                        skill_hash STRING,
                        PRIMARY KEY (skill_id)
                    )
                    """
                )
            except Exception:
                pass

    def save_skill(self, skill) -> None:
        if self.repo.read_only:
            raise RuntimeError(
                "KùzuDB está en modo read-only; no se puede guardar skill"
            )
        payload = json.dumps(skill.source_causal_hashes)
        self.repo.conn.execute(
            """
            MERGE (s:Skill {skill_id: $sid})
            SET s.yaml_payload = $yaml,
                s.source_causal_hashes = $sources,
                s.skill_hash = $hash
            """,
            {
                "sid": skill.skill_id,
                "yaml": skill.yaml_payload,
                "sources": payload,
                "hash": skill.skill_hash,
            },
        )

    def get_skill_by_id(self, skill_id: str):
        from brain.domain.memory.models import CrystallizedSkill

        result = self.repo.conn.execute(
            "MATCH (s:Skill {skill_id: $sid}) RETURN s.yaml_payload, s.source_causal_hashes, s.skill_hash",
            {"sid": skill_id},
        )
        if not result.has_next():
            return None
        row = result.get_next()
        return CrystallizedSkill(
            skill_id=skill_id,
            yaml_payload=row[0],
            source_causal_hashes=json.loads(row[1] or "[]"),
            skill_hash=row[2],
        )

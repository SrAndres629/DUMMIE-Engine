import kuzu
import zstd
import os
import json
import hashlib
import base64
from typing import Optional, List
from brain.domain.memory.ports import IEventStorePort, IStructuralAnalysisPort, ISkillRepositoryPort
from brain.domain.memory.models import MemoryNode4DTES
from brain.domain.context.models import SixDimensionalContext

class KuzuRepository(IEventStorePort, IStructuralAnalysisPort):
    """
    Implementación del repositorio 4D-TES utilizando KùzuDB (Spec 02).
    Soporta persistencia Merkle-DAG y análisis estructural de grafos.
    """
    def __init__(self, db_path: str = ".aiwg/memory/loci.db"):
        self.db_path = db_path
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
            
        self.db = kuzu.Database(self.db_path)
        self.conn = kuzu.Connection(self.db)
        self._initialize_schema()

    def _initialize_schema(self):
        """Inicializa las tablas y relaciones si no existen (Spec 02)."""
        try:
            # Nodo principal de memoria 4D-TES
            self.conn.execute("""
                CREATE NODE TABLE MemoryNode4D(
                    causal_hash STRING,
                    parent_hash STRING,
                    locus_x STRING,
                    locus_y STRING,
                    locus_z STRING,
                    lamport_t INT64,
                    authority_a STRING,
                    intent_i STRING,
                    payload STRING,
                    payload_hash STRING,
                    PRIMARY KEY (causal_hash)
                )
            """)
            
            # Nodos de Dominio (Spec 02)
            self.conn.execute("CREATE NODE TABLE Agent(id STRING, name STRING, PRIMARY KEY (id))")
            self.conn.execute("CREATE NODE TABLE Requirement(id STRING, spec STRING, PRIMARY KEY (id))")

            # Relaciones Merkle-DAG (Spec 02)
            self.conn.execute("CREATE REL TABLE CAUSED_BY(FROM MemoryNode4D TO MemoryNode4D)")
            self.conn.execute("CREATE REL TABLE EXECUTED_BY(FROM MemoryNode4D TO Agent)")
            self.conn.execute("CREATE REL TABLE VALIDATES(FROM MemoryNode4D TO Requirement)")
            
            print(f"[KuzuRepository] Esquema L2_Brain (Spec 02 FULL) inicializado en {self.db_path}")
        except Exception:
            # Asumimos que ya existe
            pass

    def append(self, node: MemoryNode4DTES) -> bool:
        """Persiste un nodo 4D-TES en el grafo."""
        try:
            # Asegurar que el payload son bytes para compresión (Spec 02)
            raw_payload = node.payload
            if isinstance(raw_payload, str):
                raw_payload = raw_payload.encode('utf-8')
                
            compressed_payload = zstd.compress(raw_payload)
            # Codificar en Base64 para persistencia como STRING (evita problemas de Binder con BLOB)
            b64_payload = base64.b64encode(compressed_payload).decode('utf-8')
            
            query = """
            CREATE (m:MemoryNode4D {
                causal_hash: $ch, 
                parent_hash: $ph, 
                payload: $py, 
                payload_hash: $pyh,
                locus_x: $lx,
                locus_y: $ly,
                locus_z: $lz,
                lamport_t: $lt,
                authority_a: $aa,
                intent_i: $ii
            })
            """
            self.conn.execute(query, {
                "ch": node.causal_hash,
                "ph": node.parent_hash,
                "py": b64_payload,
                "pyh": node.payload_hash,
                "lx": node.context.locus_x,
                "ly": node.context.locus_y,
                "lz": node.context.locus_z,
                "lt": node.context.lamport_t,
                "aa": node.context.authority_a,
                "ii": node.context.intent_i
            })
            
            # Crear arcos de causalidad (Spec 02)
            if node.parent_hash != "GENESIS":
                self.conn.execute(
                    "MATCH (p:MemoryNode4D {causal_hash: $ph}), (c:MemoryNode4D {causal_hash: $ch}) CREATE (c)-[:CAUSED_BY]->(p)",
                    {"ph": node.parent_hash, "ch": node.causal_hash}
                )
            return True
        except Exception as e:
            print(f"[KuzuRepository] Error al persistir nodo: {e}")
            return False

    def get_by_hash(self, causal_hash: str) -> Optional[MemoryNode4DTES]:
        """Recupera un nodo por su hash causal."""
        result = self.conn.execute(
            "MATCH (m:MemoryNode4D {causal_hash: $ch}) RETURN m.*",
            {"ch": causal_hash}
        )
        if result.has_next():
            row = result.get_next()
            # Decompress and decode Base64
            b64_payload = row[8]
            compressed = base64.b64decode(b64_payload)
            payload = zstd.decompress(compressed)
            
            return MemoryNode4DTES(
                causal_hash=row[0],
                parent_hash=row[1],
                payload=payload,
                payload_hash=row[9],
                context=SixDimensionalContext(
                    locus_x=row[2],
                    locus_y=row[3],
                    locus_z=row[4],
                    lamport_t=row[5],
                    authority_a=row[6],
                    intent_i=row[7]
                )
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

    def get_causal_chain(self, leaf_hash: str) -> List[MemoryNode4DTES]:
        """Reconstruye la cadena de causalidad desde una hoja hasta la raíz."""
        chain = []
        current_hash = leaf_hash
        while current_hash != "GENESIS":
            node = self.get_by_hash(current_hash)
            if not node: break
            chain.append(node)
            current_hash = node.parent_hash
        return chain

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
        while result.has_next():
            row = result.get_next()
            impacted_loci.append({
                "locus_x": row[0],
                "locus_y": row[1],
                "nodes_count": row[2]
            })
            
        return {
            "root_hash": causal_hash,
            "impact_level": "HIGH" if len(impacted_loci) > 5 else "LOW",
            "impacted_loci": impacted_loci,
            "total_impacted_nodes": len(impacted_loci)
        }


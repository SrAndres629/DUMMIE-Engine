import kuzu
import os
import json
import hashlib
import zstd
from typing import Optional, List
from brain.domain.memory.ports import IEventStorePort
from brain.domain.memory.models import MemoryNode4DTES
from brain.domain.context.models import SixDimensionalContext

class KuzuRepository(IEventStorePort):
    """
    Adaptador de Infraestructura para KùzuDB (ADR-0011 / Spec 02)
    Gestiona la persistencia causal en el Palacio de Loci.
    """
    def __init__(self, db_path: str = ".aiwg/memory/loci.db"):
        self.db_path = db_path
        # Asegurar que el directorio de persistencia existe
        db_dir = os.path.dirname(self.db_path)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        
        self.db = kuzu.Database(self.db_path)
        self.conn = kuzu.Connection(self.db)
        self._initialize_schema()

    def _initialize_schema(self):
        """Inicializa el esquema ontológico si no existe."""
        try:
            # Nodo base de Memoria 4D-TES
            self.conn.execute("CREATE NODE TABLE MemoryNode4D(causal_hash STRING, parent_hash STRING, payload STRING, payload_hash STRING, locus_x STRING, locus_y STRING, locus_z STRING, lamport_t INT64, authority_a STRING, intent_i STRING, PRIMARY KEY (causal_hash))")
            
            # Nodos de Dominio (Spec 02)
            self.conn.execute("CREATE NODE TABLE Event(id STRING, description STRING, PRIMARY KEY (id))")
            self.conn.execute("CREATE NODE TABLE Agent(id STRING, role STRING, PRIMARY KEY (id))")
            self.conn.execute("CREATE NODE TABLE Requirement(id STRING, status STRING, PRIMARY KEY (id))")
            
            # Relaciones Causales
            self.conn.execute("CREATE REL TABLE CAUSED_BY(FROM MemoryNode4D TO MemoryNode4D)")
            self.conn.execute("CREATE REL TABLE EXECUTED_BY(FROM Event TO Agent)")
            self.conn.execute("CREATE REL TABLE VALIDATES(FROM MemoryNode4D TO Requirement)")
            
            print(f"[KuzuRepository] Esquema L2_Brain inicializado en {self.db_path}")
        except Exception as e:
            if "already exists" in str(e):
                pass # Esquema ya presente
            else:
                print(f"[KuzuRepository] Error al inicializar esquema: {e}")

    def append(self, node: MemoryNode4DTES) -> bool:
        """Persiste un nodo 4D-TES en el grafo."""
        try:
            # Comprimir payload con Zstd (Spec 02)
            compressed_payload = zstd.compress(node.payload)
            
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
                "py": compressed_payload.hex(),
                "pyh": node.payload_hash,
                "lx": node.context.locus_x,
                "ly": node.context.locus_y,
                "lz": node.context.locus_z,
                "lt": node.context.lamport_t,
                "aa": node.context.authority_a.value,
                "ii": node.context.intent_i.value
            })
            
            # Si hay un padre, crear la relación CAUSED_BY
            if node.parent_hash and node.parent_hash != "GENESIS":
                self.conn.execute(
                    "MATCH (child:MemoryNode4D {causal_hash: $ch}), (parent:MemoryNode4D {causal_hash: $ph}) CREATE (child)-[:CAUSED_BY]->(parent)",
                    {"ch": node.causal_hash, "ph": node.parent_hash}
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
        if not result.has_next():
            return None
            
        row = result.get_next()
        # Mapeo manual de columnas (Kuzu no devuelve dict por defecto en versiones antiguas, asumiendo orden)
        # m.causal_hash, m.parent_hash, m.payload, m.payload_hash, m.locus_x, m.locus_y, m.locus_z, m.lamport_t, m.authority_a, m.intent_i
        
        # Descomprimir payload
        decompressed_payload = zstd.decompress(bytes.fromhex(row[2]))
        
        context = SixDimensionalContext(
            locus_x=row[4], locus_y=row[5], locus_z=row[6],
            lamport_t=row[7], authority_a=row[8], intent_i=row[9]
        )
        
        return MemoryNode4DTES(
            causal_hash=row[0],
            parent_hash=row[1],
            context=context,
            payload=decompressed_payload,
            payload_hash=row[3]
        )

    def get_causal_chain(self, leaf_hash: str, depth: int = 30) -> List[MemoryNode4DTES]:
        """
        Recupera la cadena causal hacia atrás (Merkle-DAG) usando recursión de Kùzu.
        """
        # Traer el nodo hoja primero
        leaf = self.get_by_hash(leaf_hash)
        if not leaf:
            return []

        chain = [leaf]
        
        # Traer ancestros recursivamente
        query = f"""
        MATCH (leaf:MemoryNode4D {{causal_hash: $ch}})-[*1..{depth}]->(ancestor:MemoryNode4D)
        RETURN ancestor.*
        """
        result = self.conn.execute(query, {"ch": leaf_hash})
        
        while result.has_next():
            row = result.get_next()
            decompressed_payload = zstd.decompress(bytes.fromhex(row[2]))
            context = SixDimensionalContext(
                locus_x=row[4], locus_y=row[5], locus_z=row[6],
                lamport_t=row[7], authority_a=row[8], intent_i=row[9]
            )
            node = MemoryNode4DTES(
                causal_hash=row[0],
                parent_hash=row[1],
                context=context,
                payload=decompressed_payload,
                payload_hash=row[3]
            )
            chain.append(node)
            
        # Ordenar por Lamport Tick para consistencia temporal
        chain.sort(key=lambda n: n.context.lamport_t)
        return chain

    def get_last_leaf_hash(self, locus_x: str = None) -> str:
        """Recupera el hash del nodo más reciente (head) de la cadena."""
        query = "MATCH (m:MemoryNode4D) "
        if locus_x:
            query += "WHERE m.locus_x = $lx "
        query += "RETURN m.causal_hash ORDER BY m.lamport_t DESC LIMIT 1"
        
        result = self.conn.execute(query, {"lx": locus_x} if locus_x else {})
        if not result.has_next():
            return "GENESIS"
        return result.get_next()[0]

from brain.domain.memory.ports import ISkillRepositoryPort
from brain.domain.memory.models import CrystallizedSkill

class KuzuSkillRepository(ISkillRepositoryPort):
    """
    Adaptador de Infraestructura para persistir Skills en KùzuDB (Spec 38).
    Permite trazar la proveniencia desde la Skill hasta los nodos 4D-TES.
    """
    def __init__(self, kuzu_repo: KuzuRepository):
        self.repo = kuzu_repo
        self._initialize_skill_schema()

    def _initialize_skill_schema(self):
        try:
            self.repo.conn.execute("CREATE NODE TABLE Skill(skill_id STRING, yaml_payload STRING, skill_hash STRING, PRIMARY KEY (skill_id))")
            self.repo.conn.execute("CREATE REL TABLE DERIVED_FROM(FROM Skill TO MemoryNode4D)")
        except Exception as e:
            if "already exists" not in str(e):
                print(f"[KuzuSkillRepository] Error de esquema: {e}")

    def save_skill(self, skill: CrystallizedSkill) -> None:
        """Persiste la skill y crea los enlaces de proveniencia en el grafo."""
        try:
            self.repo.conn.execute(
                "CREATE (s:Skill {skill_id: $id, yaml_payload: $pl, skill_hash: $sh})",
                {"id": skill.skill_id, "pl": skill.yaml_payload, "sh": skill.skill_hash}
            )
            
            # Enlazar con los nodos fuente (Proveniencia Causal)
            for ch in skill.source_causal_hashes:
                self.repo.conn.execute(
                    "MATCH (s:Skill {skill_id: $id}), (m:MemoryNode4D {causal_hash: $ch}) CREATE (s)-[:DERIVED_FROM]->(m)",
                    {"id": skill.skill_id, "ch": ch}
                )
        except Exception as e:
            print(f"[KuzuSkillRepository] Error al guardar skill: {e}")

    def get_skill_by_id(self, skill_id: str) -> Optional[CrystallizedSkill]:
        result = self.repo.conn.execute(
            "MATCH (s:Skill {skill_id: $id}) OPTIONAL MATCH (s)-[:DERIVED_FROM]->(m) RETURN s.*, m.causal_hash",
            {"id": skill_id}
        )
        if not result.has_next():
            return None
        
        # Agregación manual de hashes de proveniencia
        hashes = []
        skill_data = None
        
        while result.has_next():
            row = result.get_next()
            if not skill_data:
                skill_data = row[:3]
            if row[3]:
                hashes.append(row[3])
        
        return CrystallizedSkill(
            skill_id=skill_data[0],
            yaml_payload=skill_data[1],
            skill_hash=skill_data[2],
            source_causal_hashes=hashes
        )

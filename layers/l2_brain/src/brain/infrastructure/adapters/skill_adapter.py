import kuzu
from typing import Optional
from brain.domain.memory.models import CrystallizedSkill
from brain.domain.memory.ports import ISkillRepositoryPort

class KuzuSkillRepository(ISkillRepositoryPort):
    """
    Repositorio de Habilidades Cristalizadas (Spec 38).
    Almacena contratos YAML en una tabla específica del grafo.
    """
    def __init__(self, db_path: str = ".aiwg/memory/loci.db", db: kuzu.Database = None):
        self.db_path = db_path
        self.read_only = False
        
        if db is not None:
            self.db = db
        else:
            try:
                self.db = kuzu.Database(db_path)
            except RuntimeError as e:
                if "Could not set lock on file" in str(e):
                    self.db = kuzu.Database(db_path, read_only=True)
                    self.read_only = True
                else:
                    raise
        self.conn = kuzu.Connection(self.db)
        if not self.read_only:
            self._init_schema()

    def _init_schema(self):
        try:
            self.conn.execute("CREATE NODE TABLE Skill(skill_id STRING, yaml_payload STRING, skill_hash STRING, PRIMARY KEY (skill_id))")
        except Exception:
            pass # Ya existe

    def save_skill(self, skill: CrystallizedSkill) -> None:
        if self.read_only:
            raise RuntimeError(
                f"KùzuDB está en modo read-only (posible lock de otro proceso) para {self.db_path}"
            )
        self.conn.execute(
            "INSERT INTO Skill(skill_id, yaml_payload, skill_hash) VALUES ($id, $payload, $hash)",
            {"id": skill.skill_id, "payload": skill.yaml_payload, "hash": skill.skill_hash},
        )

    def get_skill_by_id(self, skill_id: str) -> Optional[CrystallizedSkill]:
        query = "MATCH (s:Skill) WHERE s.skill_id = $id RETURN s.skill_id, s.yaml_payload, s.skill_hash"
        result = self.conn.execute(query, {"id": skill_id})
        if result.has_next():
            row = result.get_next()
            return CrystallizedSkill(
                skill_id=row[0],
                yaml_payload=row[1],
                skill_hash=row[2]
            )
        return None

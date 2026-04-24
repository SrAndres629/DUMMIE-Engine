import kuzu
from typing import Optional
from brain.domain.memory.models import CrystallizedSkill
from brain.domain.memory.ports import ISkillRepositoryPort

class KuzuSkillRepository(ISkillRepositoryPort):
    """
    Repositorio de Habilidades Cristalizadas (Spec 38).
    Almacena contratos YAML en una tabla específica del grafo.
    """
    def __init__(self, db_path: str = ".aiwg/memory/loci.db"):
        self.db = kuzu.Database(db_path)
        self.conn = kuzu.Connection(self.db)
        self._init_schema()

    def _init_schema(self):
        try:
            self.conn.execute("CREATE NODE TABLE Skill(skill_id STRING, yaml_payload STRING, skill_hash STRING, PRIMARY KEY (skill_id))")
        except Exception:
            pass # Ya existe

    def save_skill(self, skill: CrystallizedSkill) -> None:
        try:
            self.conn.execute(
                "INSERT INTO Skill(skill_id, yaml_payload, skill_hash) VALUES ($id, $payload, $hash)",
                {"id": skill.skill_id, "payload": skill.yaml_payload, "hash": skill.skill_hash}
            )
        except Exception as e:
            print(f"[KuzuSkillRepository] Error al guardar skill: {e}")

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

import sys
import os
import kuzu
import hashlib

# Set up PYTHONPATH
sys.path.append("/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain/src")

from brain.infrastructure.adapters.skill_adapter import KuzuSkillRepository
from brain.domain.memory.models import CrystallizedSkill

KUZU_DB_PATH = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/loci.db"
YAML_PATH = "/home/jorand/Escritorio/DUMMIE Engine/.agents/skills/diagram_generator/skill.yaml"

def register_skill():
    db = kuzu.Database(KUZU_DB_PATH)
    repo = KuzuSkillRepository(db_path=KUZU_DB_PATH, db=db)
    
    with open(YAML_PATH, "r") as f:
        yaml_content = f.read()
    
    skill_hash = hashlib.sha256(yaml_content.encode()).hexdigest()
    
    skill = CrystallizedSkill(
        skill_id="sw.arch.diagram_generator",
        yaml_payload=yaml_content,
        skill_hash=skill_hash,
        source_causal_hashes=[] # No causal nodes for this manual deployment
    )
    
    try:
        repo.save_skill(skill)
        print(f"Skill {skill.skill_id} registered successfully in KùzuDB.")
    except Exception as e:
        if "duplicate key" in str(e).lower():
            print(f"Skill {skill.skill_id} already exists in DB.")
        else:
            print(f"Error registering skill: {e}")

if __name__ == "__main__":
    register_skill()

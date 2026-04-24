import sys
import os
import kuzu

# Set up PYTHONPATH
sys.path.append("/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain/src")

from brain.infrastructure.adapters.skill_adapter import KuzuSkillRepository
from brain.domain.fabrication.models import SkillDefinition

KUZU_DB_PATH = "/home/jorand/Escritorio/DUMMIE Engine/.aiwg/memory/loci.db"

def register_skill():
    db = kuzu.Database(KUZU_DB_PATH)
    repo = KuzuSkillRepository(db_path=KUZU_DB_PATH, db=db)
    
    skill = SkillDefinition(
        skill_name="sw.arch.diagram_generator",
        version="1.0.0",
        parameters={
            "engine": "mermaid",
            "theme": "dark",
            "format": "svg"
        }
    )
    
    # KuzuSkillRepository doesn't seem to have a 'register' method in my previous view, 
    # let me check its methods again.
    print(dir(repo))

if __name__ == "__main__":
    register_skill()

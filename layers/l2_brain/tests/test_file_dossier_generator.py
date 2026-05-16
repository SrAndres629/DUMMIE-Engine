import json
import pytest
from pathlib import Path
from layers.l2_brain.file_dossier_generator import FileDossierGenerator

@pytest.fixture
def file_env(tmp_path):
    repo = tmp_path
    aiwg = repo / ".aiwg"
    intel = aiwg / "repo_intelligence"
    intel.mkdir(parents=True)
    
    # Create actual file to test AST
    module_path = repo / "layers" / "l2_brain" / "module.py"
    module_path.parent.mkdir(parents=True)
    module_path.write_text("class MyBrain:\n  def think(self): pass\n")
    
    inventory = {
        "files": [
            {"path": "layers/l2_brain/module.py", "language": "python", "layer": "l2_brain", "is_runtime": True},
            {"path": "layers/l2_brain/tests/test_module.py", "language": "python", "layer": "l2_brain", "is_test": True}
        ]
    }
    (intel / "repo_inventory.json").write_text(json.dumps(inventory))
    return repo, aiwg

def test_generate_file_dossiers(file_env):
    repo, aiwg = file_env
    gen = FileDossierGenerator(repo_root=repo, aiwg_root=aiwg.name)
    res = gen.generate_file_dossiers()
    
    assert res["decision"] == "PASS"
    assert res["deep_dossier_count"] == 1
    assert res["standard_dossier_count"] == 1
    
    dossier_file = aiwg / "repo_intelligence" / "files" / "layers_l2_brain_module_py.json"
    assert dossier_file.exists()
    dossier = json.loads(dossier_file.read_text())
    assert dossier["tier"] == "deep"
    assert "MyBrain" in dossier["ast_summary"].get("classes", [])

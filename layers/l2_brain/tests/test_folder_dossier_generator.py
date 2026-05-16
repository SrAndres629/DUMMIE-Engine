import json
import pytest
from pathlib import Path
from layers.l2_brain.folder_dossier_generator import FolderDossierGenerator

@pytest.fixture
def dossier_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    intel = aiwg / "repo_intelligence"
    intel.mkdir(parents=True)
    
    inventory = {
        "files": [
            {"path": "layers/l2_brain/module.py", "language": "python", "layer": "l2_brain"},
            {"path": "layers/l2_brain/tests/test_module.py", "language": "python", "layer": "l2_brain"}
        ]
    }
    (intel / "repo_inventory.json").write_text(json.dumps(inventory))
    return aiwg

def test_generate_folder_dossiers(dossier_env):
    gen = FolderDossierGenerator(aiwg_root=dossier_env)
    res = gen.generate_folder_dossiers()
    
    assert res["decision"] == "PASS"
    assert len(res["dossiers"]) > 0
    assert res["dossiers"][0]["folder_path"] == "layers/l2_brain"
    assert res["dossiers"][0]["file_count"] == 2

import json
import pytest
from pathlib import Path
from layers.l2_brain.technical_debt_intelligence import TechnicalDebtIntelligence

@pytest.fixture
def debt_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    intel = aiwg / "repo_intelligence"
    intel.mkdir(parents=True)
    
    inventory = {
        "files": [
            {"path": "layers/l2_brain/untested_module.py", "language": "python", "is_runtime": True},
            {"path": "doc/specs/121_state_coherence_guard.md", "is_spec": True}
        ]
    }
    (intel / "repo_inventory.json").write_text(json.dumps(inventory))
    return aiwg

def test_detects_missing_tests(debt_env):
    gen = TechnicalDebtIntelligence(aiwg_root=debt_env)
    res = gen.run_technical_debt_intelligence()
    
    assert res["decision"] == "PASS"
    finding_ids = [f["finding_id"] for f in res["findings"]]
    assert "missing_tests_runtime" in finding_ids
    assert "malformed_spec_frontmatter" in finding_ids

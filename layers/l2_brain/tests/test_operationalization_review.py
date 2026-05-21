import json
import pytest
from pathlib import Path
from layers.l2_brain.governance.operationalization_review import OperationalizationReview

@pytest.fixture
def op_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    (aiwg / "reports").mkdir(parents=True)
    
    (aiwg / "reports" / "spec_frontmatter_repair_latest.json").write_text(json.dumps({"decision": "PASS", "repaired_count": 10}))
    (aiwg / "reports" / "context_enforcement_gate_latest.json").write_text(json.dumps({"decision": "ALLOW_DOSSIER_CONTEXT"}))
    (aiwg / "reports" / "repo_intelligence_query_latest.json").write_text(json.dumps({"decision": "PASS"}))
    
    return aiwg

def test_operationalization_review(op_env):
    reviewer = OperationalizationReview(aiwg_root=op_env)
    res = reviewer.run_operationalization_review()
    assert res["decision"] == "PASS"
    ids = [f["id"] for f in res["findings"]]
    assert "frontmatter_repaired" in ids
    assert "context_gate_active" in ids

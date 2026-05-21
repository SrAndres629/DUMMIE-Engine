import json
import pytest
from pathlib import Path
from layers.l2_brain.mission.plan_v1_completion_review import PlanV1CompletionReview

@pytest.fixture
def review_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    return aiwg

def test_plan_v1_completion_review(review_env):
    gen = PlanV1CompletionReview(aiwg_root=review_env)
    res = gen.run_plan_v1_completion_review()
    
    assert res["decision"] == "PASS"
    assert res["capabilities_scored"] > 20
    
    scorecard = json.loads((review_env / "reports" / "plan_v1_runtime_capability_scorecard.json").read_text())
    assert scorecard["decision"] == "PASS"
    caps = [c["capability_id"] for c in scorecard["capabilities"]]
    assert "repo_intelligence_runtime" in caps
    assert "trusted_workstation_mode" in caps

import json
import pytest
from pathlib import Path
from layers.l2_brain.mission.repo_intelligence_query import RepoIntelligenceQueryRuntime

@pytest.fixture
def query_env(tmp_path):
    aiwg = tmp_path / ".aiwg"
    intel = aiwg / "repo_intelligence"
    intel.mkdir(parents=True)
    
    inventory = {
        "files": [
            {"path": "layers/l2_brain/module.py", "language": "python", "layer": "l2_brain", "is_runtime": True},
            {"path": "layers/l2_brain/tests/test_module.py", "language": "python", "layer": "l2_brain", "is_test": True},
            {"path": "doc/specs/spec1.md", "is_spec": True}
        ]
    }
    (intel / "repo_inventory.json").write_text(json.dumps(inventory))
    return aiwg

def test_query_by_layer(query_env):
    runtime = RepoIntelligenceQueryRuntime(aiwg_root=query_env)
    res = runtime.query_repo_intelligence({"layer": "l2_brain"})
    assert res.count == 2

def test_query_runtime_modules(query_env):
    runtime = RepoIntelligenceQueryRuntime(aiwg_root=query_env)
    res = runtime.query_repo_intelligence({"is_runtime": True})
    assert res.count == 1
    assert res.results[0]["path"] == "layers/l2_brain/module.py"

def test_query_untested_runtime(query_env):
    runtime = RepoIntelligenceQueryRuntime(aiwg_root=query_env)
    # Filter for runtime AND no tests
    res = runtime.query_repo_intelligence({"is_runtime": True, "no_tests": True})
    assert res.count == 0
    
    # Add an untested one
    with open(query_env / "repo_intelligence" / "repo_inventory.json", "r+") as f:
        data = json.load(f)
        data["files"].append({"path": "layers/l2_brain/untested.py", "language": "python", "is_runtime": True})
        f.seek(0)
        json.dump(data, f)
        f.truncate()
        
    res = runtime.query_repo_intelligence({"is_runtime": True, "no_tests": True})
    assert res.count == 1
    assert res.results[0]["path"] == "layers/l2_brain/untested.py"

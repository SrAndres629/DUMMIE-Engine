import json
import pytest
from pathlib import Path
from layers.l2_brain.mission.repo_intelligence_runtime import RepoIntelligenceRuntime

@pytest.fixture
def repo_env(tmp_path):
    repo = tmp_path
    aiwg = tmp_path / ".aiwg"
    aiwg.mkdir()
    # Note: git ls-files won't work in a non-git tmp repo by default unless we init it
    import subprocess
    subprocess.run(["git", "init"], cwd=repo, check=True)
    
    (repo / "layers" / "l2_brain").mkdir(parents=True)
    (repo / "layers" / "l2_brain" / "test_module.py").write_text("def my_func(): pass")
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    
    return repo, aiwg

def test_repo_intel_scan(repo_env):
    repo, aiwg = repo_env
    runtime = RepoIntelligenceRuntime(repo_root=repo, aiwg_root=aiwg.name)
    res = runtime.run_repo_intelligence_scan()
    
    assert res["decision"] == "PASS"
    assert res["tracked_files_count"] >= 1
    assert "l2_brain" in res["layers_detected"]
    assert "python" in res["languages_detected"]

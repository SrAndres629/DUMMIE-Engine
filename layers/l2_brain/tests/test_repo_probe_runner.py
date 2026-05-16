import json
import pytest
import subprocess
from pathlib import Path
from layers.l2_brain.repo_probe_runner import RepoProbeRunner

@pytest.fixture
def temp_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    aiwg = repo / ".aiwg"
    aiwg.mkdir()
    (aiwg / "reports").mkdir()
    
    # Create some files
    (repo / "layers/l2_brain").mkdir(parents=True)
    (repo / "layers/l2_brain/cli_control_plane.py").touch()
    (repo / "layers/l2_brain/state_coherence_guard.py").touch()
    (repo / "layers/l2_brain/embedding_adapter.py").touch()
    
    (repo / "doc/specs").mkdir(parents=True)
    (repo / "doc/specs/test.md").touch()
    (repo / "doc/specs/test.feature").touch()
    (repo / "doc/specs/test.rules.json").touch()
    
    (repo / "tests").mkdir()
    (repo / "tests/test_dummy.py").touch()
    
    # Mock git
    import subprocess
    subprocess.run(["git", "init"], cwd=repo)
    subprocess.run(["git", "add", "."], cwd=repo)
    
    return repo

def test_repo_probe_detects_layers(temp_repo):
    runner = RepoProbeRunner(root=temp_repo)
    # We need to mock state_coherence_guard_latest.json to avoid ERROR in probe
    (temp_repo / ".aiwg/reports/state_coherence_guard_latest.json").write_text(json.dumps({"decision": "PASS"}))
    
    result = runner.run_all_probes()
    assert result.decision in ["PASS", "PASS_WITH_WARNINGS"]
    assert result.layer_summary["L2"] > 0
    assert result.runtime_summary["layers/l2_brain/cli_control_plane.py"] == "PRESENT"

def test_repo_probe_detects_incomplete_triplets(temp_repo):
    (temp_repo / "doc/specs/incomplete.md").touch()
    subprocess.run(["git", "add", "."], cwd=temp_repo)
    
    runner = RepoProbeRunner(root=temp_repo)
    (temp_repo / ".aiwg/reports/state_coherence_guard_latest.json").write_text(json.dumps({"decision": "PASS"}))
    
    result = runner.run_all_probes()
    assert any("incomplete.md" in f.message for f in result.findings)

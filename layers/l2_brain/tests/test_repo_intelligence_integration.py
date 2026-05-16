import json
import pytest
import subprocess
from pathlib import Path
from layers.l2_brain.repo_intelligence_runtime import run_repo_intelligence_scan
from layers.l2_brain.folder_dossier_generator import generate_folder_dossiers
from layers.l2_brain.file_dossier_generator import generate_file_dossiers
from layers.l2_brain.technical_debt_intelligence import run_technical_debt_intelligence
from layers.l2_brain.plan_v1_completion_review import run_plan_v1_completion_review

def test_repo_intelligence_integration(tmp_path):
    repo = tmp_path
    aiwg = tmp_path / ".aiwg"
    aiwg.mkdir()
    
    subprocess.run(["git", "init"], cwd=repo, check=True)
    
    # Create mock repo structure
    (repo / "layers" / "l2_brain" / "tests").mkdir(parents=True)
    (repo / "layers" / "l2_brain" / "module.py").write_text("class Test:\n pass")
    (repo / "layers" / "l2_brain" / "tests" / "test_module.py").write_text("def test_it(): pass")
    (repo / "doc" / "specs").mkdir(parents=True)
    (repo / "doc" / "specs" / "121_state_coherence_guard.md").write_text("# spec")
    
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    
    repo_res = run_repo_intelligence_scan(repo_root=repo, aiwg_root=aiwg.name)
    assert repo_res.decision == "PASS"
    
    folder_res = generate_folder_dossiers(aiwg_root=aiwg)
    assert folder_res.decision == "PASS"
    
    file_res = generate_file_dossiers(repo_root=repo, aiwg_root=aiwg.name)
    assert file_res.decision == "PASS"
    
    debt_res = run_technical_debt_intelligence(aiwg_root=aiwg)
    assert debt_res.decision == "PASS"
    
    review_res = run_plan_v1_completion_review(aiwg_root=aiwg)
    assert review_res.decision == "PASS"
    
    # Verify outputs
    assert (aiwg / "repo_intelligence" / "repo_inventory.json").exists()
    assert (aiwg / "repo_intelligence" / "repo_intelligence_manifest.json").exists()
    assert (aiwg / "reports" / "plan_v1_completion_review.json").exists()

# Spec Reference: 186_dependency_reproducibility_verifier
import os
import json
from pathlib import Path
from layers.l2_brain.governance.dependency_reproducibility_verifier import run_dependency_reproducibility_verification

# Spec Reference: 186_dependency_reproducibility_verifier

def test_dependency_reproducibility_verifier():
    report = run_dependency_reproducibility_verification()
    
    assert "decision" in report
    assert report["decision"] in ["PASS", "PASS_WITH_WARNINGS", "FAIL"]
    assert "installed_packages" in report
    assert "declared_packages" in report
    assert "warnings" in report
    assert "reproducibility_status" in report
    
    # Assert JSON file is created successfully
    aiwg_root = Path(__file__).resolve().parents[3] / ".aiwg"
    json_path = aiwg_root / "reports" / "dependency_reproducibility_latest.json"
    md_path = aiwg_root / "reports" / "dependency_reproducibility_latest.md"
    
    assert json_path.exists()
    assert md_path.exists()

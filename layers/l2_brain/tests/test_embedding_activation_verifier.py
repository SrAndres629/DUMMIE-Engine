# Spec Reference: 188_embedding_activation_verifier
import os
import json
from pathlib import Path
from layers.l2_brain.embedding_mesh.embedding_activation_verifier import run_embedding_activation_verification

# Spec Reference: 188_embedding_activation_verifier

def test_embedding_activation_verifier():
    report = run_embedding_activation_verification()
    
    assert "decision" in report
    assert report["decision"] in ["PASS", "PASS_WITH_WARNINGS"]
    assert "sentence_transformers_importable" in report
    assert "torch_importable" in report
    assert "embedding_mode" in report
    
    # Assert JSON file is created successfully
    aiwg_root = Path(__file__).resolve().parents[3] / ".aiwg"
    json_path = aiwg_root / "reports" / "embedding_activation_verification_latest.json"
    md_path = aiwg_root / "reports" / "embedding_activation_verification_latest.md"
    
    assert json_path.exists()
    assert md_path.exists()

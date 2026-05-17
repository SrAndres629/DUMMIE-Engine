# Spec Reference: 187_kuzu_graph_readback_verifier
import os
import json
from pathlib import Path
from layers.l2_brain.kuzu_graph_readback_verifier import run_kuzu_graph_readback_verification

# Spec Reference: 187_kuzu_graph_readback_verifier

def test_kuzu_graph_readback_verifier():
    report = run_kuzu_graph_readback_verification()
    
    assert "decision" in report
    assert report["decision"] in ["PASS", "PASS_WITH_WARNINGS", "FAIL"]
    assert "kuzu_importable" in report
    assert "sandbox_write_readback_ok" in report
    assert "promotion_recommendation" in report
    
    # Assert JSON file is created successfully
    aiwg_root = Path(__file__).resolve().parents[3] / ".aiwg"
    json_path = aiwg_root / "reports" / "kuzu_graph_readback_verification_latest.json"
    md_path = aiwg_root / "reports" / "kuzu_graph_readback_verification_latest.md"
    
    assert json_path.exists()
    assert md_path.exists()

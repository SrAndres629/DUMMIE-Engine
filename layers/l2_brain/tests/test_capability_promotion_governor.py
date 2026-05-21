# Spec Reference: 189_capability_promotion_governor
import os
import json
from pathlib import Path
from layers.l2_brain.governance.capability_promotion_governor import run_capability_promotion_governor

# Spec Reference: 189_capability_promotion_governor

def test_capability_promotion_governor():
    # Make sure dependency verifiers have run and generated reports first
    from layers.l2_brain.governance.dependency_reproducibility_verifier import run_dependency_reproducibility_verification
    from layers.l2_brain.memory.kuzu_graph_readback_verifier import run_kuzu_graph_readback_verification
    from layers.l2_brain.embedding_mesh.embedding_activation_verifier import run_embedding_activation_verification
    
    run_dependency_reproducibility_verification()
    run_kuzu_graph_readback_verification()
    run_embedding_activation_verification()

    report = run_capability_promotion_governor()
    
    assert "decision" in report
    assert report["decision"] in ["PASS", "FAIL"]
    assert "capabilities" in report
    
    # Assert JSON file is created successfully
    aiwg_root = Path(__file__).resolve().parents[3] / ".aiwg"
    json_path = aiwg_root / "reports" / "capability_promotion_governor_latest.json"
    md_path = aiwg_root / "reports" / "capability_promotion_governor_latest.md"
    
    assert json_path.exists()
    assert md_path.exists()

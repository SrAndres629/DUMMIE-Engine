# Spec Reference: 190_full_body_operational_auditor
import os
import json
from pathlib import Path
from layers.l2_brain.governance.full_body_operational_auditor import run_full_body_operational_audit

# Spec Reference: 190_full_body_operational_auditor

def test_full_body_operational_auditor():
    # Make sure governor has run
    from layers.l2_brain.governance.capability_promotion_governor import run_capability_promotion_governor
    run_capability_promotion_governor()

    report = run_full_body_operational_audit()
    
    assert "decision" in report
    assert report["decision"] in ["PASS", "PASS_WITH_WARNINGS"]
    assert "body_score" in report
    assert 0.0 <= report["body_score"] <= 100.0
    assert "organs" in report
    assert "ready_organs" in report
    
    # Assert JSON file is created successfully
    aiwg_root = Path(__file__).resolve().parents[3] / ".aiwg"
    json_path = aiwg_root / "reports" / "full_body_operational_audit_latest.json"
    md_path = aiwg_root / "reports" / "full_body_operational_audit_latest.md"
    
    assert json_path.exists()
    assert md_path.exists()

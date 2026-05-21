# Spec Reference: 191_whole_body_repair_queue
import os
import json
from pathlib import Path
from layers.l2_brain.governance.whole_body_repair_queue import run_whole_body_repair_queue

# Spec Reference: 191_whole_body_repair_queue

def test_whole_body_repair_queue():
    # Make sure governor has run
    from layers.l2_brain.governance.capability_promotion_governor import run_capability_promotion_governor
    run_capability_promotion_governor()

    report = run_whole_body_repair_queue()
    
    assert "decision" in report
    assert report["decision"] == "PASS"
    assert "actions" in report
    assert len(report["actions"]) > 0
    
    # Assert JSON file is created successfully
    aiwg_root = Path(__file__).resolve().parents[3] / ".aiwg"
    json_path = aiwg_root / "reports" / "whole_body_repair_queue_latest.json"
    md_path = aiwg_root / "reports" / "whole_body_repair_queue_latest.md"
    
    assert json_path.exists()
    assert md_path.exists()

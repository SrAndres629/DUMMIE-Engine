import json
from pathlib import Path
from epistemic_state_runtime import build_epistemic_state

def test_epistemic_state_confidence_low_on_degraded(tmp_path):
    aiwg_root = tmp_path / ".aiwg"
    reports_root = aiwg_root / "reports"
    reports_root.mkdir(parents=True)

    readiness_file = reports_root / "readiness_score_calibration_latest.json"
    readiness_file.write_text(json.dumps({
        "findings": [
            {"id": "score_1_with_degraded_kuzu", "description": "Kuzu is degraded"}
        ]
    }))

    res = build_epistemic_state("test", aiwg_root=aiwg_root)
    # Confidence should be lowered if readiness report has degraded Kuzu
    assert res.confidence < 1.0
    assert "Unresolved epistemic debt" in str(res.warnings)

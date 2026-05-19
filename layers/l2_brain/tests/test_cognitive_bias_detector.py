import json
import pytest
from cognitive_bias_detector import detect_cognitive_biases, CognitiveBiasReport

def test_bias_detection_direct(tmp_path):
    """Verify that cognitive bias detector correctly identifies multiple biases with rigorous checks."""
    # Test premature scaling bias
    res_synthesis = detect_cognitive_biases("skill synthesis", aiwg_root=tmp_path)
    assert isinstance(res_synthesis, CognitiveBiasReport)
    assert res_synthesis.decision == "FAIL"
    assert any(f["bias"] == "premature_scaling_bias" for f in res_synthesis.findings)

    # Test overconfidence bias by setting up mock files
    reports_dir = tmp_path / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    q_data = {"quality_score": 95}
    r_data = {"calibrated_scores": {"daily_use_readiness": 5}}
    
    (reports_dir / "metacognitive_quality_gate_latest.json").write_text(json.dumps(q_data))
    (reports_dir / "readiness_score_calibration_latest.json").write_text(json.dumps(r_data))
    
    res_overconfidence = detect_cognitive_biases("some standard task", aiwg_root=tmp_path)
    assert res_overconfidence.decision == "FAIL"
    assert any(f["bias"] == "overconfidence_bias" for f in res_overconfidence.findings)
    
    # Test pass scenario by changing values
    q_data["quality_score"] = 50
    (reports_dir / "metacognitive_quality_gate_latest.json").write_text(json.dumps(q_data))
    
    res_pass_actual = detect_cognitive_biases("some standard task", aiwg_root=tmp_path)
    assert res_pass_actual.decision == "PASS"
    assert len(res_pass_actual.findings) == 0

"""Tests for evolution_delta_applier.py — Pack 5.2.2"""
import json, tempfile, shutil
from pathlib import Path
from evolution_delta_applier import apply_evolution_delta


def _setup_aiwg(tmp: Path):
    aiwg = tmp / ".aiwg"
    (aiwg / "reports").mkdir(parents=True)
    (aiwg / "reports" / "metacognitive_evolution_delta_latest.json").write_text(json.dumps({
        "belief_changed": "From 'System is ready' to 'System has epistemic debt'",
        "evidence_source": "readiness_score_calibration_latest.json",
        "revision_type": "humility_calibration",
        "next_check_recommended": "repair_kuzu_persistence"
    }))
    (aiwg / "reports" / "cognitive_bias_report_latest.json").write_text(json.dumps({
        "decision": "FAIL",
        "findings": [{"bias": "premature_scaling_bias", "message": "System is not ready"}]
    }))
    (aiwg / "reports" / "mental_model_truth_hygiene_latest.json").write_text(json.dumps({
        "summary": {"quarantined_count": 2, "needs_review_count": 5, "overconfidence_count": 2}
    }))
    return aiwg


def test_generates_repair_kuzu_action():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        res = apply_evolution_delta(aiwg_root=aiwg)
        actions = res.get("actions", [])
        assert any(a["action_type"] == "repair_kuzu_persistence" for a in actions)
        repair = [a for a in actions if a["action_type"] == "repair_kuzu_persistence"][0]
        assert repair["priority"] == "critical"
    finally:
        shutil.rmtree(tmp)


def test_blocks_autonomous_scaling():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        res = apply_evolution_delta(aiwg_root=aiwg)
        actions = res.get("actions", [])
        scaling = [a for a in actions if a["action_type"] == "autonomous_scaling"]
        assert len(scaling) > 0
        assert all(a["status"] == "blocked" for a in scaling)
    finally:
        shutil.rmtree(tmp)


def test_outputs_parse_as_json():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        apply_evolution_delta(aiwg_root=aiwg)
        json.loads((aiwg / "reports" / "evolution_delta_application_latest.json").read_text())
    finally:
        shutil.rmtree(tmp)

"""Tests for self_improvement_runtime.py — Pack 5.2.2"""
import json, tempfile, shutil
from pathlib import Path
from self_improvement_runtime import run_self_improvement_cycle


def _setup_aiwg(tmp: Path):
    aiwg = tmp / ".aiwg"
    mm = aiwg / "mental_models"
    mm.mkdir(parents=True)
    (aiwg / "reports").mkdir(parents=True)
    # Create minimal models
    models = [
        {"model_id": "mm-si1", "intent": "autonomous synthesis kuzu degraded", "quality_score": 100,
         "relations": [], "assumptions": [], "decisions": [], "contradictions": [],
         "falsification_tests": [], "evidence_refs": [], "created_at": "2026-01-01"},
        {"model_id": "mm-si2", "intent": "test", "quality_score": 70,
         "relations": [{"source": "A", "target": "B", "type": "x"}],
         "assumptions": ["a"], "decisions": ["d"], "contradictions": [],
         "falsification_tests": ["f"], "evidence_refs": ["e"], "created_at": "2026-01-02"},
    ]
    (mm / "runtime_models.jsonl").write_text("\n".join(json.dumps(m) for m in models) + "\n")
    (mm / "runtime_model_index.json").write_text(json.dumps({m["model_id"]: ".aiwg/mental_models/runtime_models.jsonl" for m in models}))
    (aiwg / "reports" / "readiness_score_calibration_latest.json").write_text(json.dumps({
        "findings": [{"id": "score_1_with_degraded_kuzu", "description": "Kuzu degraded"}]
    }))
    (aiwg / "reports" / "metacognitive_evolution_delta_latest.json").write_text(json.dumps({
        "belief_changed": "From 'System is ready' to 'System has epistemic debt'",
        "evidence_source": "readiness_score_calibration_latest.json",
        "revision_type": "humility_calibration",
        "next_check_recommended": "repair_kuzu_persistence"
    }))
    (aiwg / "reports" / "cognitive_bias_report_latest.json").write_text(json.dumps({
        "decision": "PASS", "findings": []
    }))
    return aiwg


def test_produces_action_queue():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        res = run_self_improvement_cycle(aiwg_root=aiwg)
        assert len(res.get("action_queue", [])) > 0
    finally:
        shutil.rmtree(tmp)


def test_blocks_autonomous_scaling_while_kuzu_degraded():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        res = run_self_improvement_cycle(aiwg_root=aiwg)
        assert res.get("autonomous_scaling_blocked") is True
    finally:
        shutil.rmtree(tmp)


def test_next_action_is_evidence_based():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        res = run_self_improvement_cycle(aiwg_root=aiwg)
        assert res.get("next_self_improvement_action", "") != ""
    finally:
        shutil.rmtree(tmp)


def test_outputs_parse_as_json():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = _setup_aiwg(tmp)
        run_self_improvement_cycle(aiwg_root=aiwg)
        for name in ["self_improvement_cycle_latest.json", "self_improvement_action_queue.json"]:
            json.loads((aiwg / "reports" / name).read_text())
    finally:
        shutil.rmtree(tmp)

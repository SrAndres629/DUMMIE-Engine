"""Tests for mental_model_truth_hygiene.py — Pack 5.2.2"""
import json, tempfile, shutil
from pathlib import Path
from mental_model_truth_hygiene import run_mental_model_truth_hygiene


def _setup_aiwg(tmp: Path, models: list, readiness_degraded: bool = True):
    aiwg = tmp / ".aiwg"
    (aiwg / "mental_models").mkdir(parents=True)
    (aiwg / "reports").mkdir(parents=True)
    jsonl = aiwg / "mental_models" / "runtime_models.jsonl"
    jsonl.write_text("\n".join(json.dumps(m) for m in models) + "\n")
    index = {m["model_id"]: ".aiwg/mental_models/runtime_models.jsonl" for m in models}
    (aiwg / "mental_models" / "runtime_model_index.json").write_text(json.dumps(index))
    if readiness_degraded:
        (aiwg / "reports" / "readiness_score_calibration_latest.json").write_text(json.dumps({
            "findings": [{"id": "score_1_with_degraded_kuzu", "description": "Kuzu degraded"}]
        }))
    return aiwg


def test_quarantines_overconfident_model():
    tmp = Path(tempfile.mkdtemp())
    try:
        models = [{"model_id": "mm-bad1", "intent": "refactor memory", "quality_score": 100,
                    "relations": [{"source": "A", "target": "B", "type": "x"}],
                    "assumptions": [], "decisions": [], "contradictions": [],
                    "falsification_tests": [], "evidence_refs": [], "created_at": "2026-01-01"}]
        aiwg = _setup_aiwg(tmp, models, readiness_degraded=True)
        res = run_mental_model_truth_hygiene(aiwg_root=aiwg)
        assert res["summary"]["quarantined_count"] >= 1
        assert res["summary"]["overconfidence_count"] >= 1
    finally:
        shutil.rmtree(tmp)


def test_marks_empty_relations_complex_as_needs_review():
    tmp = Path(tempfile.mkdtemp())
    try:
        models = [{"model_id": "mm-weak1", "intent": "decide autonomous synthesis while kuzu degraded",
                    "quality_score": 70, "relations": [], "assumptions": [], "decisions": [],
                    "contradictions": [], "falsification_tests": [], "evidence_refs": [], "created_at": "2026-01-01"}]
        aiwg = _setup_aiwg(tmp, models)
        res = run_mental_model_truth_hygiene(aiwg_root=aiwg)
        assert res["summary"]["needs_review_count"] >= 1
    finally:
        shutil.rmtree(tmp)


def test_enriches_index_without_deleting():
    tmp = Path(tempfile.mkdtemp())
    try:
        models = [
            {"model_id": "mm-a1", "intent": "test", "quality_score": 70,
             "relations": [], "assumptions": [], "decisions": [], "contradictions": [],
             "falsification_tests": [], "evidence_refs": [], "created_at": "2026-01-01"},
            {"model_id": "mm-a2", "intent": "test", "quality_score": 80,
             "relations": [{"source": "A", "target": "B", "type": "x"}],
             "assumptions": ["a"], "decisions": ["d"], "contradictions": [],
             "falsification_tests": ["f"], "evidence_refs": ["e"], "created_at": "2026-01-02"},
        ]
        aiwg = _setup_aiwg(tmp, models, readiness_degraded=False)
        run_mental_model_truth_hygiene(aiwg_root=aiwg)
        index = json.loads((aiwg / "mental_models" / "runtime_model_index.json").read_text())
        assert "mm-a1" in index
        assert "mm-a2" in index
        assert isinstance(index["mm-a1"], dict)
        assert "status" in index["mm-a1"]
    finally:
        shutil.rmtree(tmp)


def test_outputs_parse_as_json():
    tmp = Path(tempfile.mkdtemp())
    try:
        models = [{"model_id": "mm-j1", "intent": "test", "quality_score": 50,
                    "relations": [], "assumptions": [], "decisions": [], "contradictions": [],
                    "falsification_tests": [], "evidence_refs": [], "created_at": "2026-01-01"}]
        aiwg = _setup_aiwg(tmp, models)
        run_mental_model_truth_hygiene(aiwg_root=aiwg)
        for name in ["runtime_model_hygiene.json", "runtime_model_quarantine.json", "runtime_model_lineage.json"]:
            json.loads((aiwg / "mental_models" / name).read_text())
        json.loads((aiwg / "reports" / "mental_model_truth_hygiene_latest.json").read_text())
    finally:
        shutil.rmtree(tmp)

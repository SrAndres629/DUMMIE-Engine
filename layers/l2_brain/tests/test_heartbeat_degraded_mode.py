import json
import shutil
import tempfile
from pathlib import Path

from heartbeat.heartbeat_lifecycle_runtime import run_heartbeat


def test_degraded_mode_skips_non_critical_phases():
    tmp = Path(tempfile.mkdtemp())
    try:
        aiwg = tmp / ".aiwg"
        (aiwg / "reports").mkdir(parents=True)
        (aiwg / "reports" / "readiness_score_calibration_latest.json").write_text(
            json.dumps(
                {
                    "findings": [{"id": "degraded", "description": "degraded"}],
                    "calibrated_scores": {"overall": 50.0},
                }
            ),
            encoding="utf-8",
        )
        (aiwg / "reports" / "mental_model_truth_hygiene_latest.json").write_text(
            json.dumps({"summary": {}}), encoding="utf-8"
        )
        (aiwg / "reports" / "self_improvement_action_queue.json").write_text(
            json.dumps({"actions": [], "next": ""}), encoding="utf-8"
        )
        result = run_heartbeat(mode="advisory", aiwg_root=aiwg)
        assert result["runtime_closure_plan"].get("degraded_mode") is True
        assert "metacognitive_loop" in result.get("skipped_non_critical", [])
    finally:
        shutil.rmtree(tmp)

import json
from pathlib import Path

from scripts.validate_accelerated_batch_plan import validate_plan


def test_accelerated_plan_validation_passes_current_plan():
    repo_root = Path.cwd()
    plan_path = repo_root / ".aiwg" / "reports" / "accelerated_hardening_batch_plan_latest.json"
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    result = validate_plan(plan, repo_root)
    assert result.status == "PASS"
    assert result.summary["should_execute_now_true_count"] == 0


def test_accelerated_plan_validation_detects_unsafe_flag(tmp_path):
    plan = {
        "plan_id": "x",
        "phase": "y",
        "generated_at": "z",
        "generated_from_commit": "a",
        "analysis_base_commit": "b",
        "pack_2_2_closure_commit": "c",
        "governance": {
            "no_force_push": True,
            "no_file_delete": True,
            "no_file_move": True,
            "planning_only_no_batch_execution": True,
        },
        "baseline_metrics": {},
        "batches": [
            {
                "batch_id": "B1",
                "name": "n",
                "target_count": 1,
                "risk_before": "HIGH",
                "expected_risk_after": "MEDIUM",
                "files": ["README.md"],
                "commands": ["echo ok"],
                "rollback": "git restore README.md",
                "tests": ["echo test"],
                "done_criteria": "c",
                "estimated_blast_radius": "LOW",
                "should_execute_now": True,
            }
        ],
    }
    (tmp_path / "README.md").write_text("x", encoding="utf-8")
    result = validate_plan(plan, tmp_path)
    assert result.status == "FAIL"
    assert any(e.startswith("should_execute_now_true_count") for e in result.errors)

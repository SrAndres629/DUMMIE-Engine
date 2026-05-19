#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REQUIRED_TOP_LEVEL = {
    "plan_id",
    "phase",
    "generated_at",
    "generated_from_commit",
    "analysis_base_commit",
    "pack_2_2_closure_commit",
    "governance",
    "baseline_metrics",
    "batches",
}

REQUIRED_BATCH_KEYS = {
    "batch_id",
    "name",
    "target_count",
    "risk_before",
    "expected_risk_after",
    "files",
    "commands",
    "rollback",
    "tests",
    "done_criteria",
    "estimated_blast_radius",
    "should_execute_now",
}


@dataclass
class ValidationResult:
    status: str
    errors: list[str]
    warnings: list[str]
    summary: dict[str, Any]



def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))



def validate_plan(plan: dict[str, Any], repo_root: Path) -> ValidationResult:
    errors: list[str] = []
    warnings: list[str] = []

    missing_top = sorted(REQUIRED_TOP_LEVEL - set(plan.keys()))
    if missing_top:
        errors.append(f"missing_top_level_keys:{','.join(missing_top)}")

    batches = plan.get("batches", [])
    if not isinstance(batches, list) or not batches:
        errors.append("batches_missing_or_empty")
        batches = []

    should_execute_now_true = 0
    missing_files_count = 0

    for idx, batch in enumerate(batches):
        if not isinstance(batch, dict):
            errors.append(f"batch_{idx}_invalid_type")
            continue

        missing_batch = sorted(REQUIRED_BATCH_KEYS - set(batch.keys()))
        if missing_batch:
            errors.append(f"batch_{idx}_missing_keys:{','.join(missing_batch)}")

        if batch.get("should_execute_now") is True:
            should_execute_now_true += 1

        files = batch.get("files", [])
        if not isinstance(files, list) or not files:
            errors.append(f"batch_{idx}_files_missing_or_empty")
        else:
            for rel in files:
                if not isinstance(rel, str):
                    errors.append(f"batch_{idx}_non_string_file_entry")
                    continue
                if not (repo_root / rel).exists():
                    missing_files_count += 1
                    warnings.append(f"missing_target_file:{rel}")

        for key in ("commands", "tests"):
            val = batch.get(key)
            if not isinstance(val, list) or not val:
                errors.append(f"batch_{idx}_{key}_missing_or_empty")

        rollback = batch.get("rollback", "")
        if not isinstance(rollback, str) or not rollback.strip():
            errors.append(f"batch_{idx}_rollback_missing")

    governance = plan.get("governance", {})
    if not isinstance(governance, dict):
        errors.append("governance_invalid_type")
    else:
        for hard_lock in (
            "no_force_push",
            "no_file_delete",
            "no_file_move",
            "planning_only_no_batch_execution",
        ):
            if governance.get(hard_lock) is not True:
                warnings.append(f"governance_lock_not_true:{hard_lock}")

    if should_execute_now_true > 0:
        errors.append(f"should_execute_now_true_count:{should_execute_now_true}")

    status = "PASS" if not errors else "FAIL"
    return ValidationResult(
        status=status,
        errors=errors,
        warnings=sorted(set(warnings)),
        summary={
            "batches": len(batches),
            "should_execute_now_true_count": should_execute_now_true,
            "missing_files_count": missing_files_count,
        },
    )



def write_reports(result: ValidationResult, reports_dir: Path) -> None:
    reports_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "status": result.status,
        "errors": result.errors,
        "warnings": result.warnings,
        "summary": result.summary,
    }
    json_path = reports_dir / "accelerated_hardening_batch_plan_validation_latest.json"
    md_path = reports_dir / "accelerated_hardening_batch_plan_validation_latest.md"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        "# Accelerated Batch Plan Validation",
        "",
        f"- status: {result.status}",
        f"- batches: {result.summary.get('batches', 0)}",
        f"- should_execute_now_true_count: {result.summary.get('should_execute_now_true_count', 0)}",
        f"- missing_files_count: {result.summary.get('missing_files_count', 0)}",
        "",
        "## Errors",
    ]
    if result.errors:
        for e in result.errors:
            lines.append(f"- {e}")
    else:
        lines.append("- none")

    lines.append("")
    lines.append("## Warnings")
    if result.warnings:
        for w in result.warnings:
            lines.append(f"- {w}")
    else:
        lines.append("- none")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")



def main() -> int:
    parser = argparse.ArgumentParser(description="Validate accelerated hardening batch plan")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--plan-path",
        default=".aiwg/reports/accelerated_hardening_batch_plan_latest.json",
    )
    parser.add_argument("--write-reports", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    plan_path = (root / args.plan_path).resolve()
    plan = _load_json(plan_path)
    result = validate_plan(plan, root)

    if args.write_reports:
        write_reports(result, root / ".aiwg" / "reports")

    return 0 if result.status == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())

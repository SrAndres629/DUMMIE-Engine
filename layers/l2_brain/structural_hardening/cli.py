from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Dict, Tuple

from .matrix import StructuralTriageMatrix, load_json_safe
from .reporter import write_reports


def build_structural_hardening_triage(
    repo_root: str,
    write_reports_flag: bool,
    max_actions: int,
    include_low_risk: bool,
    fail_on_critical: bool,
    mode: str = "write-reports",
) -> Tuple[Dict[str, Any], int]:
    root = Path(repo_root).resolve()
    reports_dir = root / ".aiwg" / "reports"

    semantic_index = load_json_safe(reports_dir / "semantic_repo_index_latest.json", default={"files": []})
    semantic_matrix = load_json_safe(reports_dir / "semantic_hardening_matrix_latest.json", default={"records": []})

    matrix = StructuralTriageMatrix(root)
    report = matrix.build(
        semantic_index=semantic_index,
        semantic_matrix=semantic_matrix,
        max_actions=max_actions,
        include_low_risk=include_low_risk,
    )

    if mode == "write-reports" or (mode != "dry-run" and write_reports_flag):
        write_reports(report, reports_dir, max_actions=max_actions)

    exit_code = 0
    if mode == "validate-only":
        unknowns = [f for f in report.findings if f.proposed_class.value == "UNKNOWN"]
        orphans = [f for f in report.findings if f.proposed_class.value == "ORPHAN_TEST_CANDIDATE"]
        if unknowns or orphans:
            print(f"Validation failed: found {len(unknowns)} UNKNOWNs and {len(orphans)} ORPHANs")
            exit_code = 3
        else:
            from .bindings import ContractBindingRegistry
            registry = ContractBindingRegistry()
            for binding in registry.get_all_bindings():
                _, validation = registry.evaluate(binding.path, repo_root=root, evidence={"evidence_refs": binding.evidence_refs})
                if validation and (validation.missing_spec_refs or validation.missing_test_refs or validation.missing_runtime_refs):
                    if "doc/.deprecated/" not in binding.path:
                        print(f"Validation failed: binding {binding.path} has missing references")
                        exit_code = 4
                        break

    critical = report.summary_counts.get("by_risk", {}).get("CRITICAL", 0)
    if fail_on_critical and critical > 0:
        exit_code = 2

    return report.model_dump(mode="json"), exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Structural Hardening Pack 2 triage reports")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--write-reports", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--max-actions", type=int, default=50)
    parser.add_argument("--include-low-risk", action="store_true")
    parser.add_argument("--fail-on-critical", action="store_true")
    parser.add_argument("--mode", choices=["write-reports", "dry-run", "validate-only"], default="write-reports")
    args = parser.parse_args()

    _, exit_code = build_structural_hardening_triage(
        repo_root=args.repo_root,
        write_reports_flag=args.write_reports,
        max_actions=args.max_actions,
        include_low_risk=args.include_low_risk,
        fail_on_critical=args.fail_on_critical,
        mode=args.mode,
    )
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

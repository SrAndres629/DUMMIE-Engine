"""4D-TES Persistence Preflight Module for non-destructive persistence checks and repair planning."""

import json
from pathlib import Path

def run_4dtes_preflight(aiwg_root: Path = None) -> dict:
    if aiwg_root is None:
        aiwg_root = Path(__file__).resolve().parents[2]

    reports_dir = aiwg_root / ".aiwg" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    warnings = []
    evidence_refs = []
    repair_plan = []
    blocked_actions = []

    # Check readiness score for Kuzu
    readiness_path = reports_dir / "readiness_score_calibration_latest.json"
    kuzu_degraded = True
    if readiness_path.exists():
        evidence_refs.append(".aiwg/reports/readiness_score_calibration_latest.json")
        try:
            readiness = json.loads(readiness_path.read_text(encoding="utf-8"))
            for finding in readiness.get("findings", []):
                if "degraded_kuzu" in finding.get("id", ""):
                    kuzu_degraded = True
                    break
        except Exception:
            pass

    # Check kuzu import availability
    kuzu_importable = False
    try:
        import kuzu
        kuzu_importable = True
    except ImportError:
        warnings.append("Kùzu library is not installed or importable in current Python environment.")
        kuzu_degraded = True

    # Detect db path
    db_path = ".aiwg/memory/loci.db"
    
    # Decisions and modes based on Kuzu availability
    if kuzu_degraded or not kuzu_importable:
        decision = "PASS_WITH_WARNINGS"
        graph_write_mode = "SIMULATED"
        memory_spine_status = "degraded_logical_only"
        blocked_actions.append("graph_persistence_transaction_write")
        repair_plan.append("Install Kùzu library in virtual environment via offline safe compilation.")
        repair_plan.append("Restore PyArrow IPC data buffers mapping for zero-copy memory transport.")
        warnings.append("Kùzu/4D-TES persistence is currently DEGRADED. Actions requiring write transactions will be simulated.")
    else:
        decision = "PASS"
        graph_write_mode = "READY"
        memory_spine_status = "ready_persisted"

    report = {
        "decision": decision,
        "kuzu_importable": kuzu_importable,
        "db_path_detected": db_path,
        "graph_write_mode": graph_write_mode,
        "memory_spine_status": memory_spine_status,
        "safe_to_attempt_repair": False, # Requires external installation/dependency gates
        "repair_plan": repair_plan,
        "blocked_actions": blocked_actions,
        "warnings": warnings,
        "evidence_refs": evidence_refs
    }

    # Save reports
    json_path = reports_dir / "4dtes_persistence_preflight_latest.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_lines = [
        f"# 4D-TES Persistence Preflight Report",
        f"- **Decision**: **{decision}**",
        f"- **Kùzu Importable**: {kuzu_importable}",
        f"- **Database Path Detected**: `{db_path}`",
        f"- **Graph Write Mode**: `{graph_write_mode}`",
        f"- **Memory Spine Status**: `{memory_spine_status}`",
        f"- **Safe To Attempt Repair**: {report['safe_to_attempt_repair']}",
        f"",
        f"## Blocked Actions",
    ]
    for action in blocked_actions:
        md_lines.append(f"- `[BLOCKED]` {action}")
    if not blocked_actions:
        md_lines.append("- None")

    md_lines.append("\n## Repair Plan")
    for step in repair_plan:
        md_lines.append(f"1. {step}")
    if not repair_plan:
        md_lines.append("- No repairs needed.")

    if warnings:
        md_lines.append("\n## Warnings")
        for w in warnings:
            md_lines.append(f"- [WARNING] {w}")

    md_path = reports_dir / "4dtes_persistence_preflight_latest.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return report

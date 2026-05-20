# Spec: 175_4dtes_persistence_preflight
# Spec: DE-V2-L2-175
"""4D-TES Persistence Preflight Module for non-destructive persistence checks and repair planning."""

# Spec Reference: 187_kuzu_graph_readback_verifier
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

    # Check readback verification
    readback_path = reports_dir / "kuzu_graph_readback_verification_latest.json"
    promo_path = reports_dir / "capability_promotion_governor_latest.json"
    
    kuzu_readback_pass = False
    idempotency_pass = False
    promo_rec = "DEGRADED"

    if readback_path.exists():
        evidence_refs.append(".aiwg/reports/kuzu_graph_readback_verification_latest.json")
        try:
            rb_data = json.loads(readback_path.read_text(encoding="utf-8"))
            kuzu_readback_pass = (rb_data.get("decision") == "PASS")
            idempotency_pass = (rb_data.get("idempotency_check") == "PASS")
            promo_rec = rb_data.get("promotion_recommendation", "DEGRADED")
        except Exception:
            pass

    kuzu_importable = False
    try:
        import kuzu
        kuzu_importable = True
    except ImportError:
        warnings.append("Kùzu library is not installed or importable in current Python environment.")

    db_path = ".aiwg/memory/loci.db"

    # Rules mapping:
    # If Kuzu graph readback PASS and idempotency PASS, graph_write_mode may become READY_CANDIDATE or READY.
    # If only memory_spine_sync says READY but readback not verified, remain PASS_WITH_WARNINGS.
    if kuzu_readback_pass and idempotency_pass and promo_rec in ["READY", "READY_CANDIDATE"]:
        decision = "PASS"
        graph_write_mode = promo_rec
        memory_spine_status = "ready_persisted"
    else:
        decision = "PASS_WITH_WARNINGS"
        graph_write_mode = "SIMULATED"
        memory_spine_status = "degraded_logical_only"
        blocked_actions.append("graph_persistence_transaction_write")
        repair_plan.append("Run Kuzu readback verification suite to validate loci.db.")
        warnings.append("Kùzu/4D-TES readback verification is incomplete or locked. Actions requiring write transactions will be simulated.")

    report = {
        "decision": decision,
        "kuzu_importable": kuzu_importable,
        "db_path_detected": db_path,
        "graph_write_mode": graph_write_mode,
        "memory_spine_status": memory_spine_status,
        "safe_to_attempt_repair": False,
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

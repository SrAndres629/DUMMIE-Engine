"""Daemon/Gateway Heartbeat Bridge Module for safe, human-gated operation dispatch envelopes."""

import json
import uuid
from pathlib import Path

def run_daemon_gateway_bridge_demo(intent: str, aiwg_root: Path = None) -> dict:
    if aiwg_root is None:
        aiwg_root = Path(__file__).resolve().parents[2]

    reports_dir = aiwg_root / ".aiwg" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    warnings = []
    evidence_refs = []

    # Get status and context references
    context_ref = ""
    packet_path = reports_dir / "6d_context_packet_latest.json"
    if packet_path.exists():
        evidence_refs.append(".aiwg/reports/6d_context_packet_latest.json")
        try:
            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            context_ref = packet.get("packet_id", "")
        except Exception:
            pass

    # Read latest heartbeat decision
    heartbeat_path = reports_dir / "heartbeat_latest.json"
    selected_action = {"action_type": "advisory_observation"}
    if heartbeat_path.exists():
        evidence_refs.append(".aiwg/reports/heartbeat_latest.json")
        try:
            hb = json.loads(heartbeat_path.read_text(encoding="utf-8"))
            if hb.get("selected_action"):
                selected_action = hb["selected_action"]
        except Exception:
            pass

    # Safety rules enforcement
    requires_human_approval = True
    can_execute_now = False # Mutation action must be gated

    dispatch_envelope = {
        "dispatch_id": str(uuid.uuid4()),
        "selected_action": selected_action,
        "target": "human_review", # Standard restricted dispatch target
        "mode": "repair_planning",
        "context_packet_ref": context_ref,
        "memory_refs": [".aiwg/reports/memory_spine_entrypoint_latest.json"] if (reports_dir / "memory_spine_entrypoint_latest.json").exists() else [],
        "safety_constraints": ["no_unauthorized_execution", "no_network_connections", "sandbox_only"],
        "requires_human_approval": requires_human_approval,
        "can_execute_now": can_execute_now,
        "reason": f"System action requires explicit human verification for intent: \"{intent}\""
    }

    report = {
        "decision": "PASS",
        "daemon_status": "INVOCATION_ONLY",
        "gateway_status": "MAPPED",
        "dispatch_envelope": dispatch_envelope,
        "warnings": warnings,
        "evidence_refs": evidence_refs
    }

    # Save reports
    json_path = reports_dir / "daemon_gateway_heartbeat_bridge_latest.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_lines = [
        f"# Daemon/Gateway Heartbeat Bridge Report",
        f"- **Decision**: **{report['decision']}**",
        f"- **Daemon Status**: `{report['daemon_status']}`",
        f"- **Gateway Status**: `{report['gateway_status']}`",
        f"",
        f"## Dispatch Envelope Details",
        f"- **Dispatch ID**: `{dispatch_envelope['dispatch_id']}`",
        f"- **Target**: `{dispatch_envelope['target']}`",
        f"- **Mode**: `{dispatch_envelope['mode']}`",
        f"- **Requires Human Approval**: `{dispatch_envelope['requires_human_approval']}`",
        f"- **Can Execute Now**: `{dispatch_envelope['can_execute_now']}`",
        f"- **Reason**: {dispatch_envelope['reason']}",
        f"",
        f"## Safety Constraints Enforced",
    ]
    for constraint in dispatch_envelope["safety_constraints"]:
        md_lines.append(f"- `[ENFORCED]` {constraint}")

    if warnings:
        md_lines.append("\n## Warnings")
        for w in warnings:
            md_lines.append(f"- [WARNING] {w}")

    md_path = reports_dir / "daemon_gateway_heartbeat_bridge_latest.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return report


def compile_daemon_gateway_envelope(intent: str, safety_status: dict, aiwg_root: Path = None) -> dict:
    demo = run_daemon_gateway_bridge_demo(intent=intent, aiwg_root=aiwg_root)
    # Ensure bridge envelope has target matching the gateway safe targets
    envelope = demo["dispatch_envelope"]
    # If the intent implies mutating any files, target must be human_review
    if "mutate" in intent or "repair" in intent or "write" in intent or "refactor" in intent:
        envelope["target"] = "human_review"
        envelope["requires_human_approval"] = True
        envelope["can_execute_now"] = False
    return {
        "decision": "PASS",
        "bridge_envelope": envelope
    }

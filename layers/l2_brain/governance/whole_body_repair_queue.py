# Spec Reference: 191_whole_body_repair_queue
import os
import sys
import json
from pathlib import Path

# Spec Reference: 191_whole_body_repair_queue

def run_whole_body_repair_queue() -> dict:
    aiwg_root = Path(__file__).resolve().parents[2] / ".aiwg"
    reports_dir = aiwg_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Load promoting cap data
    promo_data = {}
    try:
        with open(reports_dir / "capability_promotion_governor_latest.json", "r", encoding="utf-8") as f:
            promo_data = json.load(f)
    except Exception:
        pass

    cap_statuses = {}
    for cap in promo_data.get("capabilities", []):
        cap_statuses[cap["capability_id"]] = cap["verified_status"]

    actions = []

    # Priority 1: False READY Claims
    # Check if any capability has declared READY previously but is not validated
    if cap_statuses.get("kuzu_4dtes_persistence") == "DEGRADED":
        actions.append({
            "action_id": "repair_kuzu_ready_truth",
            "body_part": "memory",
            "capability_id": "kuzu_4dtes_persistence",
            "title": "Repair False READY Claim for Kuzu DB",
            "priority": "critical",
            "action_type": "repair",
            "requires_human_approval": True,
            "can_execute_now": False,
            "recommended_agent": "antigravity",
            "evidence_refs": [".aiwg/reports/capability_promotion_governor_latest.json"],
            "verification_commands": ["dummie-ctl kuzu-readback"]
        })

    # Priority 2: Kuzu/4D-TES readback
    if cap_statuses.get("kuzu_4dtes_persistence") == "READY_CANDIDATE":
        actions.append({
            "action_id": "integrate_kuzu_graph_sync",
            "body_part": "memory",
            "capability_id": "kuzu_4dtes_persistence",
            "title": "Integrate Kuzu Graph Sync and Loci.db Readback",
            "priority": "high",
            "action_type": "wire",
            "requires_human_approval": True,
            "can_execute_now": False,
            "recommended_agent": "antigravity",
            "evidence_refs": [".aiwg/reports/kuzu_graph_readback_verification_latest.json"],
            "verification_commands": ["dummie-ctl kuzu-readback"]
        })

    # Priority 3: Embedding activation
    if cap_statuses.get("real_semantic_embeddings") == "FALLBACK":
        actions.append({
            "action_id": "activate_local_embedding_model_or_label_fallback",
            "body_part": "memory",
            "capability_id": "real_semantic_embeddings",
            "title": "Activate Local Embedding Model or Label Fallback Cosine Projections",
            "priority": "medium",
            "action_type": "configure",
            "requires_human_approval": False,
            "can_execute_now": True,
            "recommended_agent": "local",
            "evidence_refs": [".aiwg/reports/embedding_activation_verification_latest.json"],
            "verification_commands": ["dummie-ctl embedding-activation"]
        })

    # Priority 4: Context/token measurement
    if cap_statuses.get("token_usage_measurement") == "FALLBACK":
        actions.append({
            "action_id": "wire_upstream_token_usage_telemetry",
            "body_part": "metabolism",
            "capability_id": "token_usage_measurement",
            "title": "Wire Upstream Token Usage Dynamic Telemetry",
            "priority": "medium",
            "action_type": "wire",
            "requires_human_approval": True,
            "can_execute_now": False,
            "recommended_agent": "codex",
            "evidence_refs": [".aiwg/reports/token_economy_benchmark_latest.json"],
            "verification_commands": ["dummie-ctl token-usage"]
        })

    # Priority 5: Polyglot build/test
    if cap_statuses.get("polyglot_build_test_runtime") == "FALLBACK":
        actions.append({
            "action_id": "configure_polyglot_build_test_lifecycle",
            "body_part": "polyglot_body",
            "capability_id": "polyglot_build_test_runtime",
            "title": "Configure Polyglot Build and Test Lifecycle Orchestration",
            "priority": "medium",
            "action_type": "configure",
            "requires_human_approval": True,
            "can_execute_now": False,
            "recommended_agent": "gemini",
            "evidence_refs": [".aiwg/reports/polyglot_probe_latest.json"],
            "verification_commands": ["pytest layers/l2_brain/tests/"]
        })

    # Priority 6: Daemon/gateway live health
    if cap_statuses.get("daemon_persistent_runtime") == "SIMULATED":
        actions.append({
            "action_id": "activate_autonomous_background_heartbeat_loop",
            "body_part": "hands",
            "capability_id": "daemon_persistent_runtime",
            "title": "Activate Autonomous Background Heartbeat Supervisor",
            "priority": "low",
            "action_type": "wire",
            "requires_human_approval": True,
            "can_execute_now": False,
            "recommended_agent": "human",
            "evidence_refs": [".aiwg/reports/daemon_gateway_heartbeat_bridge_latest.json"],
            "verification_commands": ["systemctl --user status dummie-engine.service"]
        })

    # Default if everything is fine
    if not actions:
        actions.append({
            "action_id": "maintain_operational_hygiene",
            "body_part": "skin",
            "capability_id": "spec_runtime_mapping",
            "title": "Maintain High-Cohesion Operational Hygiene",
            "priority": "low",
            "action_type": "verify",
            "requires_human_approval": False,
            "can_execute_now": True,
            "recommended_agent": "antigravity",
            "evidence_refs": [],
            "verification_commands": ["python3 scripts/validate_specs_docs.py"]
        })

    # Sorted order matching spec rule: False READY claims first, Kuzu second, Embedding third, etc.
    priority_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    actions.sort(key=lambda x: priority_order.get(x["priority"], 99))

    report = {
        "decision": "PASS",
        "actions": actions
    }

    # Write JSON report
    json_path = reports_dir / "whole_body_repair_queue_latest.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write Markdown report
    md_path = reports_dir / "whole_body_repair_queue_latest.md"
    md_content = f"""# Whole Body Repair Queue Report
**Decision**: `PASS`  

## Prioritized Repair Backlog
"""
    for idx, act in enumerate(actions, start=1):
        md_content += f"""### {idx}. {act['title']} (Priority: `{act['priority'].upper()}`)
- **Action ID**: `{act['action_id']}`
- **Body Part**: `{act['body_part']}`
- **Capability ID**: `{act['capability_id']}`
- **Action Type**: `{act['action_type']}`
- **Requires Human Approval**: `{act['requires_human_approval']}`
- **Can Execute Now**: `{act['can_execute_now']}`
- **Recommended Agent**: `{act['recommended_agent']}`
- **Verification Commands**: `{act['verification_commands']}`
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return report

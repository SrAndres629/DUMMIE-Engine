# Spec: 181_runtime_closure_planner
# Spec: DE-V2-L2-181
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List


def run_runtime_closure_plan(aiwg_root: str = ".") -> Dict[str, Any]:
    """
    Ingests the Degraded Capability Registry and produces a comprehensive,
    human-executable, step-by-step Closure Plan for resolving each degraded module.
    """
    root_path = Path(aiwg_root).resolve()
    reports_dir = root_path.joinpath(".aiwg/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Degraded Capability Registry
    registry = {}
    reg_path = reports_dir.joinpath("degraded_capability_registry_latest.json")
    if reg_path.exists():
        try:
            with open(reg_path, "r", encoding="utf-8") as f:
                registry = json.load(f)
        except Exception:
            pass

    caps = registry.get("capabilities", [])
    actions = []

    # 2. Sequential actions generation
    for cap in caps:
        cap_id = cap.get("capability_id")
        status = cap.get("actual_status")

        if cap_id == "kuzu_4dtes_persistence" and status == "SIMULATED":
            # Add multi-step Kùzu closure sequence
            # Action 1: Install kuzu package (Must have can_execute_now: false)
            actions.append(
                {
                    "action_id": "install_kuzu_library",
                    "capability_id": cap_id,
                    "title": "Install Kùzu Python Bindings",
                    "action_type": "install_dependency",
                    "priority": "critical",
                    "can_execute_now": False,
                    "requires_human_approval": True,
                    "commands_to_run": [".venv/bin/pip install kuzu==0.7.1"],
                    "files_to_modify": [],
                    "verification_commands": [
                        ".venv/bin/python -c 'import kuzu; print(kuzu.__version__)'"
                    ],
                    "rollback_plan": [".venv/bin/pip uninstall -y kuzu"],
                    "risk_level": "medium",
                    "evidence_refs": [str(reg_path)],
                }
            )

            # Action 2: Database Path Calibration
            actions.append(
                {
                    "action_id": "configure_kuzu_db_path",
                    "capability_id": cap_id,
                    "title": "Configure Kùzu Database Directory",
                    "action_type": "configure_path",
                    "priority": "high",
                    "can_execute_now": False,
                    "requires_human_approval": True,
                    "commands_to_run": ["mkdir -p .aiwg/memory/loci.db"],
                    "files_to_modify": ["layers/l2_brain/models.py"],
                    "verification_commands": ["test -d .aiwg/memory/loci.db"],
                    "rollback_plan": [],
                    "risk_level": "low",
                    "evidence_refs": [str(reg_path)],
                }
            )

            # Action 3: Database Write / Readback Verification
            actions.append(
                {
                    "action_id": "test_kuzu_readwrite_connectivity",
                    "capability_id": cap_id,
                    "title": "Verify Non-Destructive Kùzu DB Write/Readback Sequence",
                    "action_type": "write_integration_test",
                    "priority": "high",
                    "can_execute_now": False,
                    "requires_human_approval": True,
                    "commands_to_run": [
                        ".venv/bin/python layers/l2_brain/tests/test_four_dtes_persistence_preflight.py"
                    ],
                    "files_to_modify": [],
                    "verification_commands": [],
                    "rollback_plan": [],
                    "risk_level": "medium",
                    "evidence_refs": [str(reg_path)],
                }
            )

            # Action 4: Enable Production Write Adapter Mode
            actions.append(
                {
                    "action_id": "enable_production_kuzu_adapter",
                    "capability_id": cap_id,
                    "title": "Toggle Production Kùzu Persistent Database Adapter",
                    "action_type": "enable_adapter",
                    "priority": "medium",
                    "can_execute_now": False,
                    "requires_human_approval": True,
                    "commands_to_run": [],
                    "files_to_modify": [
                        "layers/l2_brain/four_dtes_persistence_preflight.py"
                    ],
                    "verification_commands": ["dummie-ctl 4dtes-preflight"],
                    "rollback_plan": [],
                    "risk_level": "high",
                    "evidence_refs": [str(reg_path)],
                }
            )

        elif cap_id == "real_semantic_embeddings" and status == "FALLBACK":
            actions.append(
                {
                    "action_id": "configure_local_sentence_transformers",
                    "capability_id": cap_id,
                    "title": "Configure Offline Sentence Transformers Embedding Adapter",
                    "action_type": "enable_adapter",
                    "priority": "medium",
                    "can_execute_now": False,
                    "requires_human_approval": True,
                    "commands_to_run": [".venv/bin/pip install sentence-transformers"],
                    "files_to_modify": ["layers/l2_brain/embedding_memory_router.py"],
                    "verification_commands": [
                        ".venv/bin/python -c 'import sentence_transformers'"
                    ],
                    "rollback_plan": [
                        ".venv/bin/pip uninstall -y sentence-transformers"
                    ],
                    "risk_level": "medium",
                    "evidence_refs": [str(reg_path)],
                }
            )

        elif cap_id == "full_regression_suite" and status == "DEGRADED":
            actions.append(
                {
                    "action_id": "run_regression_testing",
                    "capability_id": cap_id,
                    "title": "Execute All Dynamic Test Cases and Clean Up Orphans",
                    "action_type": "run_full_regression",
                    "priority": "high",
                    "can_execute_now": False,
                    "requires_human_approval": True,
                    "commands_to_run": ["pytest layers/l2_brain/tests/"],
                    "files_to_modify": [],
                    "verification_commands": [],
                    "rollback_plan": [],
                    "risk_level": "low",
                    "evidence_refs": [str(reg_path)],
                }
            )

        elif cap_id == "shadow_module_resolution" and status == "SIMULATED":
            actions.append(
                {
                    "action_id": "archive_redundant_shadow_files",
                    "capability_id": cap_id,
                    "title": "Safely Archive and Prune Shadow/Duplicate Code Modules",
                    "action_type": "repair_mapping",
                    "priority": "low",
                    "can_execute_now": False,
                    "requires_human_approval": True,
                    "commands_to_run": [
                        "mkdir -p .aiwg/archive",
                        "mv layers/l2_brain/shadow_*.py .aiwg/archive/ || true",
                    ],
                    "files_to_modify": [],
                    "verification_commands": [],
                    "rollback_plan": [],
                    "risk_level": "medium",
                    "evidence_refs": [str(reg_path)],
                }
            )

        elif cap_id == "spec_runtime_mapping" and status == "DEGRADED":
            actions.append(
                {
                    "action_id": "generate_spec_physical_evidence",
                    "capability_id": cap_id,
                    "title": "Resolve Missing Physical Evidence Spec Audit Files",
                    "action_type": "write_integration_test",
                    "priority": "medium",
                    "can_execute_now": False,
                    "requires_human_approval": True,
                    "commands_to_run": ["python3 scripts/validate_specs_docs.py"],
                    "files_to_modify": [
                        "doc/specs/172_six_dimensional_context_runtime.md"
                    ],
                    "verification_commands": [],
                    "rollback_plan": [],
                    "risk_level": "low",
                    "evidence_refs": [str(reg_path)],
                }
            )

    # Hard invariant check: No install_dependency actions must ever be set to can_execute_now = True
    for action in actions:
        if (
            action["action_type"] == "install_dependency"
            and action["can_execute_now"] is True
        ):
            action["can_execute_now"] = False

    decision = "PASS"
    if actions:
        decision = "PASS_WITH_WARNINGS"

    report = {
        "decision": decision,
        "actions": actions,
        "evidence_refs": [str(reg_path)],
    }

    # Write JSON report
    latest_json = reports_dir.joinpath("runtime_closure_plan_latest.json")
    with open(latest_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write Markdown report
    latest_md = reports_dir.joinpath("runtime_closure_plan_latest.md")
    md_content = f"""# Runtime Closure Plan Report
**Decision**: {decision}

## Actionable Repair Steps (Human Gated)
"""
    for act in actions:
        md_content += f"### {act['title']} ({act['action_id']})\n"
        md_content += f"- **Capability**: `{act['capability_id']}`\n"
        md_content += f"- **Action Type**: `{act['action_type']}`\n"
        md_content += f"- **Priority**: {act['priority'].upper()}\n"
        md_content += f"- **Can Execute Now**: `{act['can_execute_now']}`\n"
        md_content += (
            f"- **Requires Human Approval**: `{act['requires_human_approval']}`\n"
        )
        if act["commands_to_run"]:
            md_content += f"- **Commands to Run**:\n"
            for c in act["commands_to_run"]:
                md_content += f"  - `{c}`\n"
        if act["verification_commands"]:
            md_content += f"- **Verification Commands**:\n"
            for v in act["verification_commands"]:
                md_content += f"  - `{v}`\n"
        md_content += "\n"

    with open(latest_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    return report


if __name__ == "__main__":
    run_runtime_closure_plan()

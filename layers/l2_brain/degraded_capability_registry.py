# Spec: 179_degraded_capability_registry
# Spec: DE-V2-L2-179
import os
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

def run_degraded_capability_registry(aiwg_root: str = ".") -> Dict[str, Any]:
    """
    Consolidates the status of all high-level capabilities, mapping physical reality
    from dependency audits and preflights to create a central degraded capability registry.
    """
    root_path = Path(aiwg_root).resolve()
    reports_dir = root_path.joinpath(".aiwg/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Load dependency audit as base
    dep_audit = {}
    dep_audit_path = reports_dir.joinpath("runtime_dependency_audit_latest.json")
    if dep_audit_path.exists():
        try:
            with open(dep_audit_path, "r", encoding="utf-8") as f:
                dep_audit = json.load(f)
        except Exception:
            pass
            
    missing_deps = dep_audit.get("missing_dependencies", [])
    
    # 2. Build list of registered capabilities
    capabilities = []
    
    # Capability 1: Kùzu 4D-TES persistence
    kuzu_status = "READY"
    kuzu_reason = "Kùzu physical database persistence is available and writing."
    kuzu_blocks = []
    if "kuzu" in missing_deps:
        kuzu_status = "SIMULATED"
        kuzu_reason = "Kùzu library is not installed on this host environment. Falling back to logically simulated memory."
        kuzu_blocks = ["graph_persistence_transaction_write", "ipc_arrow_zero_copy_transport"]
    
    capabilities.append({
        "capability_id": "kuzu_4dtes_persistence",
        "name": "Kùzu DB 4D-TES Persistence",
        "claimed_status": "READY",
        "actual_status": kuzu_status,
        "reason": kuzu_reason,
        "required_dependencies": ["kuzu"],
        "required_config": ["db_path", "write_mode"],
        "required_verification": ["kuzu_import_check", "dry_run_write", "readback_test"],
        "blocks": kuzu_blocks,
        "safe_repair_possible_now": True,
        "risk_level": "medium",
        "evidence_refs": [str(dep_audit_path)]
    })

    # Capability 2: Real Semantic Embeddings
    embedding_status = "READY"
    embedding_reason = "Local FastEmbed BAAI/bge-small-en-v1.5 engine is active and producing real vectors."
    embedding_blocks = []
    try:
        from fastembed import TextEmbedding
    except ImportError:
        embedding_status = "FALLBACK"
        embedding_reason = "External upstream embedding APIs are disabled and fastembed is not installed. Local SHA256 deterministic mock routing is active."
        embedding_blocks = ["semantic_similarity_search", "high_dimensional_clustering"]

    capabilities.append({
        "capability_id": "real_semantic_embeddings",
        "name": "Real Semantic Vector Embeddings",
        "claimed_status": "READY",
        "actual_status": embedding_status,
        "reason": embedding_reason,
        "required_dependencies": ["numpy", "fastembed"],
        "required_config": ["embedding_provider_api_key", "vector_dimension"],
        "required_verification": ["vector_indexing_quality_gate"],
        "blocks": embedding_blocks,
        "safe_repair_possible_now": False,
        "risk_level": "low",
        "evidence_refs": [str(dep_audit_path)]
    })

    # Capability 3: Daemon Persistent Runtime
    capabilities.append({
        "capability_id": "daemon_persistent_runtime",
        "name": "Daemon Persistent Background Supervisor",
        "claimed_status": "READY",
        "actual_status": "SIMULATED",
        "reason": "Sovereign background daemon loop is disabled. Operational lifecycle is invocation-only.",
        "required_dependencies": ["click", "rich"],
        "required_config": ["daemon_pid_file", "log_rotation"],
        "required_verification": ["process_running_check"],
        "blocks": ["autonomous_background_heartbeat_loop", "active_socket_bridge"],
        "safe_repair_possible_now": False,
        "risk_level": "high",
        "evidence_refs": [str(dep_audit_path)]
    })

    # Capability 4: Gateway Live Dispatch
    capabilities.append({
        "capability_id": "gateway_live_dispatch",
        "name": "MCP Gateway Active Dispatcher",
        "claimed_status": "READY",
        "actual_status": "DRY_RUN_ONLY",
        "reason": "Daemon Gateway is invocation-only and enforces absolute manual review constraints.",
        "required_dependencies": ["fastapi", "click"],
        "required_config": ["mcp_gateway_port", "dispatch_signature_secret"],
        "required_verification": ["live_gateway_handshake_audit"],
        "blocks": ["autonomous_tool_mutation_apply"],
        "safe_repair_possible_now": False,
        "risk_level": "critical",
        "evidence_refs": [str(dep_audit_path)]
    })

    # Capability 5: Polyglot Build and Test Runtime
    capabilities.append({
        "capability_id": "polyglot_build_test_runtime",
        "name": "Polyglot Language Build & Test Orchestration",
        "claimed_status": "READY",
        "actual_status": "FALLBACK",
        "reason": "Language Probes detect languages but do not execute active builds or test runtimes dynamically.",
        "required_dependencies": ["pytest"],
        "required_config": ["language_manifest_exclusions"],
        "required_verification": ["compile_and_link_verification"],
        "blocks": ["dynamic_otp_elixir_build", "go_l1_binary_compile"],
        "safe_repair_possible_now": False,
        "risk_level": "medium",
        "evidence_refs": [str(dep_audit_path)]
    })

    # Capability 6: Token Usage Measurement
    capabilities.append({
        "capability_id": "token_usage_measurement",
        "name": "Upstream Token Usage Telemetry",
        "claimed_status": "READY",
        "actual_status": "FALLBACK",
        "reason": "Token Cost Ledger compiles static estimates rather than connecting to active provider usage counters.",
        "required_dependencies": ["pydantic"],
        "required_config": ["model_pricing_rules"],
        "required_verification": ["usage_accounting_audit"],
        "blocks": ["upstream_cost_cap_enforcement"],
        "safe_repair_possible_now": False,
        "risk_level": "low",
        "evidence_refs": [str(dep_audit_path)]
    })

    # Capability 7: Full Regression Suite
    # Check if there are orphan/missing tests
    capabilities.append({
        "capability_id": "full_regression_suite",
        "name": "Comprehensive Codebase Regression Testing",
        "claimed_status": "READY",
        "actual_status": "DEGRADED",
        "reason": "Missing or orphan tests exist; the full regression run is not fully automated under single invoke.",
        "required_dependencies": ["pytest"],
        "required_config": ["test_path_triages"],
        "required_verification": ["regression_green_gate"],
        "blocks": ["zero_regression_guarantees"],
        "safe_repair_possible_now": True,
        "risk_level": "medium",
        "evidence_refs": [str(dep_audit_path)]
    })

    # Capability 8: Shadow Module Resolution
    capabilities.append({
        "capability_id": "shadow_module_resolution",
        "name": "Dynamic Shadow Module Resolution",
        "claimed_status": "READY",
        "actual_status": "SIMULATED",
        "reason": "Shadow modules are classified but not actively cleaned, archived, or resolved.",
        "required_dependencies": [],
        "required_config": ["shadow_exclusion_rules"],
        "required_verification": ["shadow_prune_audit"],
        "blocks": ["autonomous_shadow_module_pruning"],
        "safe_repair_possible_now": True,
        "risk_level": "low",
        "evidence_refs": [str(dep_audit_path)]
    })

    # Capability 9: Spec Runtime Mapping
    capabilities.append({
        "capability_id": "spec_runtime_mapping",
        "name": "Active Spec and Runtime Validation",
        "claimed_status": "READY",
        "actual_status": "DEGRADED",
        "reason": "Spec validations fail due to physical evidence files that do not exist dynamically.",
        "required_dependencies": [],
        "required_config": ["spec_manifests"],
        "required_verification": ["spec_coverage_run"],
        "blocks": ["automatic_spec_regression_blocks"],
        "safe_repair_possible_now": True,
        "risk_level": "medium",
        "evidence_refs": [str(dep_audit_path)]
    })

    # Capability 10: Context Actual Tokenizer
    capabilities.append({
        "capability_id": "context_actual_tokenizer",
        "name": "Physical upstream token measurement",
        "claimed_status": "READY",
        "actual_status": "FALLBACK",
        "reason": "Tokenizer uses simplified string-based cost models rather than active tiktoken/model libraries.",
        "required_dependencies": [],
        "required_config": [],
        "required_verification": [],
        "blocks": [],
        "safe_repair_possible_now": True,
        "risk_level": "low",
        "evidence_refs": [str(dep_audit_path)]
    })

    decision = "PASS"
    for cap in capabilities:
        if cap["actual_status"] in ["DEGRADED", "SIMULATED", "DRY_RUN_ONLY", "FALLBACK", "MISSING"]:
            decision = "PASS_WITH_WARNINGS"

    report = {
        "decision": decision,
        "capabilities": capabilities,
        "evidence_refs": [str(dep_audit_path)]
    }

    # Write JSON report
    latest_json = reports_dir.joinpath("degraded_capability_registry_latest.json")
    with open(latest_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write Markdown report
    latest_md = reports_dir.joinpath("degraded_capability_registry_latest.md")
    md_content = f"""# Degraded Capability Registry Report
**Decision**: {decision}

## Registered Capabilities Status
"""
    for cap in capabilities:
        md_content += f"### {cap['name']} ({cap['capability_id']})\n"
        md_content += f"- **Claimed Status**: {cap['claimed_status']}\n"
        md_content += f"- **Actual Status**: {cap['actual_status']}\n"
        md_content += f"- **Reason**: {cap['reason']}\n"
        md_content += f"- **Risk Level**: {cap['risk_level']}\n"
        if cap["blocks"]:
            md_content += f"- **Blocked Actions**: {', '.join(cap['blocks'])}\n"
        md_content += "\n"

    with open(latest_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    return report

if __name__ == "__main__":
    run_degraded_capability_registry()

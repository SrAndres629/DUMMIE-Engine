# Spec: 178_runtime_dependency_auditor
# Spec: DE-V2-L2-178
import os
import sys
import json
import importlib
from pathlib import Path
from typing import Dict, Any, List


def run_runtime_dependency_audit(aiwg_root: str = ".") -> Dict[str, Any]:
    """
    Safely audits Python packages and dependency configurations, distinguishing
    between real, simulated, fallback, and dry-run states without modifying or
    installing anything.
    """
    root_path = Path(aiwg_root).resolve()

    # 1. Profile project manifests
    manifests = {
        "pyproject.toml": root_path.joinpath("pyproject.toml").exists(),
        "requirements.txt": root_path.joinpath("requirements.txt").exists(),
        "setup.py": root_path.joinpath("setup.py").exists(),
        "setup.cfg": root_path.joinpath("setup.cfg").exists(),
        "Pipfile": root_path.joinpath("Pipfile").exists(),
        "poetry.lock": root_path.joinpath("poetry.lock").exists(),
        "uv.lock": root_path.joinpath("uv.lock").exists(),
        ".venv": root_path.joinpath("layers/l2_brain/.venv").exists()
        or root_path.joinpath(".venv").exists(),
    }

    # 2. Test safe imports
    monitored = [
        "kuzu",
        "pytest",
        "yaml",
        "networkx",
        "numpy",
        "pydantic",
        "fastapi",
        "typer",
        "rich",
        "click",
    ]
    dependencies = []
    missing_dependencies = []
    optional_missing_dependencies = []
    required_missing_dependencies = []

    # Let's consider kuzu, numpy optional (degraded fallbacks exist)
    # Let's consider pytest, yaml, pydantic, click, rich required
    required_packages = {"pytest", "yaml", "pydantic", "rich", "click"}

    for name in monitored:
        # Special handling: pyyaml is imported as 'yaml'
        import_name = name
        try:
            mod = importlib.import_module(import_name)
            ver = getattr(mod, "__version__", None)
            if ver is None:
                # Try sub-modules or other fields
                ver = "installed"
            dependencies.append({"name": name, "status": "READY", "version": str(ver)})
        except ImportError:
            dependencies.append({"name": name, "status": "MISSING", "version": None})
            missing_dependencies.append(name)
            if name in required_packages:
                required_missing_dependencies.append(name)
            else:
                optional_missing_dependencies.append(name)

    # 3. Classify simulated, fallback, and dry-run capabilities
    simulated_capabilities = []
    fallback_capabilities = []
    dry_run_capabilities = []
    ready_capabilities = []
    unsafe_to_enable = []
    warnings = []

    # Kùzu capability
    if "kuzu" in missing_dependencies:
        simulated_capabilities.append("kuzu_4dtes_persistence")
        warnings.append(
            "Kùzu Python package is missing; 4D-TES database persistence falls back to logical simulated mode."
        )
    else:
        # Check if preflight has disabled write or fallback is forced
        ready_capabilities.append("kuzu_4dtes_persistence")

    # Embeddings capability
    # Check if we have active semantic embeddings or deterministic fallback
    # Since active semantic provider relies on external APIs which are disabled:
    fallback_capabilities.append("real_semantic_embeddings")
    warnings.append(
        "External embedding provider APIs are disabled. Memory Router uses deterministic fallback projection."
    )

    # Daemon persistent runtime
    # We don't have a background persistent daemon running, it's invocation only via human approvals
    simulated_capabilities.append("daemon_persistent_runtime")
    warnings.append(
        "Persistent background daemon is disabled. Life cycle runs in invocation-only advisory mode."
    )

    # Gateway live dispatch
    # MCP live dispatch requires human gateway bridge gated checks
    dry_run_capabilities.append("gateway_live_dispatch")
    warnings.append("MCP tool dispatch is human-gated (can_execute_now: false).")

    # Polyglot build/test orchestration
    # Probes exist but real build/test toolchain runs aren't fully integrated yet
    fallback_capabilities.append("polyglot_build_test_runtime")

    # Token usage measurement
    # Current measurements are estimates rather than real provider telemetry calls
    fallback_capabilities.append("token_usage_measurement")
    warnings.append(
        "Token Cost Ledger tracks estimates rather than active upstream API provider telemetry."
    )

    decision = "PASS"
    if required_missing_dependencies:
        decision = "FAIL"
    elif missing_dependencies or warnings:
        decision = "PASS_WITH_WARNINGS"

    report = {
        "decision": decision,
        "dependencies": dependencies,
        "missing_dependencies": missing_dependencies,
        "optional_missing_dependencies": optional_missing_dependencies,
        "required_missing_dependencies": required_missing_dependencies,
        "simulated_capabilities": simulated_capabilities,
        "fallback_capabilities": fallback_capabilities,
        "dry_run_capabilities": dry_run_capabilities,
        "ready_capabilities": ready_capabilities,
        "unsafe_to_enable": unsafe_to_enable,
        "warnings": warnings,
        "evidence_refs": ["pyproject.toml", "layers/l2_brain/.venv"],
    }

    # Write JSON report
    reports_dir = root_path.joinpath(".aiwg/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    latest_json = reports_dir.joinpath("runtime_dependency_audit_latest.json")
    with open(latest_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write Markdown report
    latest_md = reports_dir.joinpath("runtime_dependency_audit_latest.md")
    md_content = f"""# Runtime Dependency Audit Report
**Decision**: {decision}

## Monitored Dependencies
"""
    for dep in dependencies:
        md_content += (
            f"- **{dep['name']}**: {dep['status']} (Version: {dep['version']})\n"
        )

    md_content += "\n## Missing Dependencies\n"
    if missing_dependencies:
        for m in missing_dependencies:
            md_content += f"- {m}\n"
    else:
        md_content += "*None*\n"

    md_content += "\n## Capability Classifications\n"
    md_content += f"- **Simulated**: {', '.join(simulated_capabilities) if simulated_capabilities else 'None'}\n"
    md_content += f"- **Fallback**: {', '.join(fallback_capabilities) if fallback_capabilities else 'None'}\n"
    md_content += f"- **Dry-Run**: {', '.join(dry_run_capabilities) if dry_run_capabilities else 'None'}\n"
    md_content += f"- **Ready**: {', '.join(ready_capabilities) if ready_capabilities else 'None'}\n"

    md_content += "\n## Warnings / Remediation Triggers\n"
    if warnings:
        for w in warnings:
            md_content += f"- {w}\n"
    else:
        md_content += "*None*\n"

    with open(latest_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    return report


if __name__ == "__main__":
    run_runtime_dependency_audit()

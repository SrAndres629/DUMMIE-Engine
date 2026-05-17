# Spec Reference: 186_dependency_reproducibility_verifier
import os
import sys
import json
import tomllib
import importlib.util
import importlib.metadata
from pathlib import Path

# Spec Reference: 186_dependency_reproducibility_verifier

def get_package_footprint(package_name: str) -> int:
    """Safely calculate total package disk size in bytes."""
    try:
        spec = importlib.util.find_spec(package_name)
        if spec and spec.origin:
            origin_path = Path(spec.origin)
            if origin_path.name == "__init__.py":
                package_dir = origin_path.parent
                total_size = 0
                for root, _, files in os.walk(package_dir):
                    for f in files:
                        fp = Path(root) / f
                        if fp.exists():
                            total_size += fp.stat().st_size
                return total_size
            else:
                return origin_path.stat().st_size
    except Exception:
        pass
    return 0

def run_dependency_reproducibility_verification() -> dict:
    aiwg_root = Path(__file__).resolve().parents[2] / ".aiwg"
    reports_dir = aiwg_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Core monitored packages
    monitored = ["kuzu", "networkx", "fastapi", "sentence_transformers", "torch"]
    
    installed_packages = []
    undeclared_installed_packages = []
    declared_packages = []
    missing_declared_packages = []
    heavy_dependencies = []
    warnings = []
    evidence_refs = [
        "layers/l2_brain/pyproject.toml",
        "layers/l2_brain/.venv"
    ]

    # Parse declared packages from pyproject.toml
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    if pyproject_path.exists():
        try:
            with open(pyproject_path, "rb") as f:
                data = tomllib.load(f)
                deps = data.get("project", {}).get("dependencies", [])
                for dep in deps:
                    # Extract package name (everything before >=, ==, <, etc.)
                    name = dep.split(">=")[0].split("==")[0].split("<")[0].split("[")[0].strip().replace("-", "_")
                    declared_packages.append(name)
        except Exception as e:
            warnings.append(f"Failed to parse pyproject.toml: {e}")
    else:
        warnings.append("pyproject.toml not found")

    # Audit physical imports
    for m in monitored:
        spec = importlib.util.find_spec(m)
        if spec:
            installed_packages.append(m)
            # Find version
            version = "unknown"
            try:
                version = importlib.metadata.version(m.replace("_", "-"))
            except Exception:
                try:
                    mod = importlib.import_module(m)
                    if hasattr(mod, "__version__"):
                        version = mod.__version__
                except Exception:
                    pass
            
            # Check heavy footprint
            size_bytes = get_package_footprint(m)
            size_mb = size_bytes / (1024 * 1024)
            if size_mb > 10.0:
                heavy_dependencies.append(f"{m} ({size_mb:.1f} MB)")
            
            # Check if declared
            if m not in declared_packages:
                undeclared_installed_packages.append(m)
        else:
            if m in declared_packages:
                missing_declared_packages.append(m)

    # Truth rule check:
    # If sentence-transformers/torch are installed but not declared in project dependency files, decision cannot be PASS.
    has_undeclared_heavy = any(x in undeclared_installed_packages for x in ["sentence_transformers", "torch"])
    
    if has_undeclared_heavy:
        decision = "FAIL"
        reproducibility_status = "BROKEN"
        warnings.append("Critical dependencies (torch/sentence_transformers) are installed but not declared in pyproject.toml!")
    elif undeclared_installed_packages:
        decision = "PASS_WITH_WARNINGS"
        reproducibility_status = "LOCAL_ONLY"
        warnings.append(f"Undeclared installed packages: {undeclared_installed_packages}")
    else:
        decision = "PASS"
        reproducibility_status = "REPRODUCIBLE"

    report = {
        "decision": decision,
        "installed_packages": installed_packages,
        "declared_packages": declared_packages,
        "undeclared_installed_packages": undeclared_installed_packages,
        "missing_declared_packages": missing_declared_packages,
        "heavy_dependencies": heavy_dependencies,
        "reproducibility_status": reproducibility_status,
        "warnings": warnings,
        "evidence_refs": evidence_refs
    }

    # Write JSON report
    json_path = reports_dir / "dependency_reproducibility_latest.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write Markdown report
    md_path = reports_dir / "dependency_reproducibility_latest.md"
    md_content = f"""# Dependency Reproducibility Audit Report
**Decision**: `{decision}`  
**Status**: `{reproducibility_status}`

## Verification Summary
- **Installed Monitored**: {installed_packages}
- **Declared Dependencies**: {declared_packages}
- **Undeclared Installed**: {undeclared_installed_packages}
- **Missing Declared**: {missing_declared_packages}
- **Heavy Dependencies (>10MB)**: {heavy_dependencies}

## Warnings
{chr(10).join(f'- {w}' for w in warnings) if warnings else 'None'}
"""
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    return report

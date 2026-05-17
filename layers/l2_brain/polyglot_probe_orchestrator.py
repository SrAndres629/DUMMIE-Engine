"""Polyglot Probe Orchestrator Module for safe, multi-language asset auditing and directory exclusions."""

import json
from pathlib import Path

def run_polyglot_probe(aiwg_root: Path = None) -> dict:
    if aiwg_root is None:
        aiwg_root = Path(__file__).resolve().parents[2]

    reports_dir = aiwg_root / ".aiwg" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    # Scans first-party manifests in workspace
    monitored_manifests = ["requirements.txt", "package.json", "Cargo.toml", "go.mod", "mix.exs"]
    found_manifests = []
    
    for manifest in monitored_manifests:
        if (aiwg_root / manifest).exists():
            found_manifests.append(manifest)

    # Scans source file extensions, respecting strict exclusions
    dependency_exclusions = [
        "node_modules", "target", ".venv", "_build", ".git", 
        "build", "dist", ".aiwg/workspaces"
    ]
    
    languages = {"python": 0, "go": 0, "elixir": 0, "rust": 0, "javascript_typescript": 0}
    first_party_files = []

    # Safe shallow traverse of workspace directory structure
    for p in aiwg_root.rglob("*"):
        if p.is_file():
            # Respect exclusions
            parts = p.relative_to(aiwg_root).parts
            if any(exc in parts for exc in dependency_exclusions):
                continue
            
            ext = p.suffix.lower()
            rel_path = str(p.relative_to(aiwg_root))
            if ext == ".py":
                languages["python"] += 1
                first_party_files.append(rel_path)
            elif ext == ".go":
                languages["go"] += 1
                first_party_files.append(rel_path)
            elif ext in (".ex", ".exs") and p.name != "mix.exs":
                languages["elixir"] += 1
                first_party_files.append(rel_path)
            elif ext == ".rs":
                languages["rust"] += 1
                first_party_files.append(rel_path)
            elif ext in (".js", ".ts", ".jsx", ".tsx") and "postcss.config" not in rel_path and "tailwind.config" not in rel_path:
                languages["javascript_typescript"] += 1
                first_party_files.append(rel_path)

    warnings = []
    decision = "PASS"
    if languages["python"] == 0:
        decision = "FAIL"
        warnings.append("No first-party Python source files detected in the workspace.")

    report = {
        "decision": decision,
        "languages": {lang: count for lang, count in languages.items() if count > 0},
        "layers": {
            "L0_supervisor": "mix.exs" in found_manifests or "go.mod" in found_manifests,
            "L1_gateway": "package.json" in found_manifests,
            "L2_brain": "requirements.txt" in found_manifests
        },
        "first_party_files": first_party_files[:50], # Sample first 50 files for report
        "dependency_exclusions": dependency_exclusions,
        "build_exclusions": ["mix_compile", "cargo_build", "npm_run_build"],
        "test_roots": [
            "layers/l2_brain/tests"
        ],
        "runtime_roles": ["cognitive_agent", "supervisor_daemon", "comms_gateway"],
        "warnings": warnings,
        "evidence_refs": [f"{m}" for m in found_manifests]
    }

    # Save reports
    json_path = reports_dir / "polyglot_probe_latest.json"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    md_lines = [
        f"# Polyglot Probe Orchestrator Report",
        f"- **Decision**: **{report['decision']}**",
        f"",
        f"## Detected Languages and File Counts",
    ]
    for lang, count in report["languages"].items():
        md_lines.append(f"- **{lang.capitalize()}**: {count} files")

    md_lines.append("\n## Architectural Layers Mapping")
    for layer, active in report["layers"].items():
        md_lines.append(f"- **{layer}**: `{'ACTIVE' if active else 'INACTIVE'}`")

    md_lines.append("\n## Dependency Exclusions Respected")
    for exc in report["dependency_exclusions"]:
        md_lines.append(f"- `[EXCLUDED]` {exc}")

    if warnings:
        md_lines.append("\n## Warnings")
        for w in warnings:
            md_lines.append(f"- [WARNING] {w}")

    md_path = reports_dir / "polyglot_probe_latest.md"
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    return report

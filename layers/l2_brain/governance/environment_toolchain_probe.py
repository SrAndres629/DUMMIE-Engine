# Spec: 180_environment_toolchain_probe
# Spec: DE-V2-L2-180
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List


def run_environment_toolchain_probe(aiwg_root: str = ".") -> Dict[str, Any]:
    """
    Safely probes the host toolchains (Python, Go, Rust, Elixir, Node, Protobuf)
    via read-only version query commands, returning robust metrics without altering anything.
    """
    root_path = Path(aiwg_root).resolve()
    reports_dir = root_path.joinpath(".aiwg/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    toolchains = {
        "python": ["python3", "--version"],
        "go": ["go", "version"],
        "rust": ["rustc", "--version"],
        "cargo": ["cargo", "--version"],
        "elixir": ["elixir", "--version"],
        "mix": ["mix", "--version"],
        "node": ["node", "--version"],
        "npm": ["npm", "--version"],
        "protobuf": ["protoc", "--version"],
    }

    results = {}
    missing_toolchains = []
    warnings = []

    for key, cmd in toolchains.items():
        try:
            # Execute command with a short 2-second timeout
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=2.0,
            )
            if proc.returncode == 0:
                ver_str = proc.stdout.strip() or proc.stderr.strip()
                results[key] = {
                    "installed": True,
                    "version": ver_str,
                    "command": " ".join(cmd),
                }
            else:
                results[key] = {
                    "installed": False,
                    "error": f"Exit code {proc.returncode}: {proc.stderr.strip()}",
                    "command": " ".join(cmd),
                }
                missing_toolchains.append(key)
                warnings.append(f"Toolchain '{key}' returned a non-zero exit code.")
        except FileNotFoundError:
            results[key] = {
                "installed": False,
                "error": "Command not found on the host system PATH.",
                "command": " ".join(cmd),
            }
            missing_toolchains.append(key)
            warnings.append(f"Toolchain '{key}' is not installed (command not found).")
        except subprocess.TimeoutExpired:
            results[key] = {
                "installed": False,
                "error": "Command timed out.",
                "command": " ".join(cmd),
            }
            missing_toolchains.append(key)
            warnings.append(f"Toolchain '{key}' version query command timed out.")
        except Exception as e:
            results[key] = {
                "installed": False,
                "error": str(e),
                "command": " ".join(cmd),
            }
            missing_toolchains.append(key)
            warnings.append(
                f"Toolchain '{key}' failed with unexpected exception: {str(e)}"
            )

    decision = "PASS"
    # Python3 must be installed since we are running!
    if not results.get("python", {}).get("installed", False):
        decision = "FAIL"
    elif missing_toolchains:
        decision = "PASS_WITH_WARNINGS"

    report = {
        "decision": decision,
        "python": results.get("python", {}),
        "go": results.get("go", {}),
        "rust": results.get("rust", {}),
        "elixir": results.get("elixir", {}),
        "node": results.get("node", {}),
        "protobuf": results.get("protobuf", {}),
        "package_managers": {
            "cargo": results.get("cargo", {}),
            "mix": results.get("mix", {}),
            "npm": results.get("npm", {}),
        },
        "missing_toolchains": missing_toolchains,
        "warnings": warnings,
        "evidence_refs": ["/usr/bin/env"],
    }

    # Write JSON report
    latest_json = reports_dir.joinpath("environment_toolchain_probe_latest.json")
    with open(latest_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    # Write Markdown report
    latest_md = reports_dir.joinpath("environment_toolchain_probe_latest.md")
    md_content = f"""# Environment Toolchain Probe Report
**Decision**: {decision}

## Monitored Toolchains
"""
    for key, value in results.items():
        status = "INSTALLED" if value.get("installed") else "MISSING"
        ver = value.get("version", "N/A")
        err = value.get("error", "")
        md_content += f"- **{key.capitalize()}**: {status}\n"
        if ver != "N/A":
            md_content += f"  - Version: `{ver}`\n"
        if err:
            md_content += f"  - Error: *{err}*\n"

    md_content += "\n## Missing Toolchains Summary\n"
    if missing_toolchains:
        md_content += f"- {', '.join(missing_toolchains)}\n"
    else:
        md_content += "*None*\n"

    with open(latest_md, "w", encoding="utf-8") as f:
        f.write(md_content)

    return report


if __name__ == "__main__":
    run_environment_toolchain_probe()

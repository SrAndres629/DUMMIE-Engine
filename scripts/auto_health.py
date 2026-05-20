#!/usr/bin/env python3
"""Auto health monitor for DUMMIE Engine.

Runs operational truth report, consolidates git state, test results,
and writes a comprehensive health.json to .aiwg/state/ for trans-session continuity.

Can be run as cron or heartbeat action.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
AIWG_STATE = REPO_ROOT / ".aiwg" / "state"
AIWG_REPORTS = REPO_ROOT / ".aiwg" / "reports"
AIWG_STRATEGIC = REPO_ROOT / ".aiwg" / "strategic"
AGENTS_MD = REPO_ROOT / "AGENTS.md"
BOOTSTRAP_MD = REPO_ROOT / "BOOTSTRAP.md"


def ensure_dirs():
    for d in [AIWG_STATE, AIWG_REPORTS, AIWG_STRATEGIC]:
        os.makedirs(str(d), exist_ok=True)


def run(cmd: list, timeout: int = 30) -> dict:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(REPO_ROOT))
        return {"returncode": r.returncode, "stdout": r.stdout.strip(), "stderr": r.stderr.strip()}
    except subprocess.TimeoutExpired:
        return {"returncode": -1, "stdout": "", "stderr": "TIMEOUT"}
    except FileNotFoundError:
        return {"returncode": -2, "stdout": "", "stderr": "NOT_FOUND"}


def git_status() -> dict:
    status = run(["git", "status", "--short"], timeout=5)
    log = run(["git", "log", "--oneline", "-5"], timeout=5)
    branch = run(["git", "branch", "--show-current"], timeout=5)
    sha = run(["git", "rev-parse", "--short", "HEAD"], timeout=5)
    return {
        "branch": branch.get("stdout", "?"),
        "sha": sha.get("stdout", "?"),
        "modified_count": len([l for l in status.get("stdout", "").split("\n") if l.strip()]),
        "modified_files": [l.strip() for l in status.get("stdout", "").split("\n") if l.strip()],
        "recent_commits": [l.strip() for l in log.get("stdout", "").split("\n") if l.strip()],
    }


def run_tests() -> dict:
    """Run pytest in-process for targeted test suites."""
    results = {"passed": 0, "failed": 0, "errors": 0, "total": 0, "failed_tests": []}
    try:
        import pytest
        test_suites = [
            (["-q", "--tb=short", "--no-header", "-k", "daemon",
              str(REPO_ROOT / "layers/l2_brain/tests/")], "daemon"),
            (["-q", "--tb=short", "--no-header",
              str(REPO_ROOT / "layers/l2_brain/tests/test_imports_compatibility.py"),
              str(REPO_ROOT / "layers/l2_brain/tests/test_causal_integrity.py")], "core"),
        ]
        for args, name in test_suites:
            exit_code = pytest.main(args, plugins=[])
            if exit_code == 0:
                results["passed"] += 1
            else:
                results["failed"] += 1
                results["failed_tests"].append(name)
    except Exception as e:
        results["errors"] = 1
        results["failed_tests"].append(str(e))
    return results


def check_bootstrap() -> dict:
    if BOOTSTRAP_MD.exists():
        return {"exists": True, "age_days": (datetime.now() - datetime.fromtimestamp(BOOTSTRAP_MD.stat().st_mtime)).days}
    return {"exists": False}


def check_redirector() -> dict:
    init_py = REPO_ROOT / "layers" / "l2_brain" / "__init__.py"
    if init_py.exists():
        content = init_py.read_text()
        has_redirector = "L2BrainRedirector" in content
        has_fallback_finder = "_FlatBrainFallbackFinder" in content
        return {"old_redirector": has_redirector, "fallback_finder": has_fallback_finder}
    return {"error": "no __init__.py"}


def check_split_brain() -> dict:
    r = run(["rg", "-nl", "class AuthorityLevel", "layers/l2_brain/"])
    files = [l for l in r.get("stdout", "").split("\n") if l.strip() and "flat_brain" not in l]
    return {"authority_files": files, "count": len(files)}


def check_env_processes() -> dict:
    ps = run(["ps", "-eo", "cmd"], timeout=5)
    lines = ps.get("stdout", "").lower()
    return {
        "dummied_running": "dummied" in lines,
        "nats_running": "nats-server" in lines,
        "ollama_running": "ollama" in lines,
        "daemon_running": "dummie-brain" in lines or "dummie_brain" in lines,
    }


def parse_test_trend(previous: dict, current: dict) -> str:
    if not previous or previous.get("tests_passed", 0) == 0:
        return "initial"
    diff = current.get("passed", 0) - previous.get("tests_passed", 0)
    if diff > 0:
        return f"improved (+{diff})"
    elif diff < 0:
        return f"regressed ({diff})"
    return "stable"


def main():
    ensure_dirs()

    previous = {}
    health_path = AIWG_STATE / "health.json"
    if health_path.exists():
        try:
            previous = json.loads(health_path.read_text())
        except (json.JSONDecodeError, OSError):
            previous = {}

    test_results = run_tests()
    gs = git_status()
    bs = check_bootstrap()
    rd = check_redirector()
    sb = check_split_brain()
    procs = check_env_processes()

    trend = parse_test_trend(previous, test_results)

    now = datetime.now(timezone.utc).isoformat()

    health = {
        "timestamp": now,
        "version": gs.get("sha", "?"),
        "branch": gs.get("branch", "?"),
        "bootstrap": bs,
        "tests_total": test_results.get("total", 0),
        "tests_passed": test_results.get("passed", 0),
        "tests_failed": test_results.get("failed", 0),
        "tests_trend": trend,
        "failed_tests": test_results.get("failed_tests", []),
        "git": {
            "modified_count": gs.get("modified_count", 0),
            "sha": gs.get("sha", "?"),
            "branch": gs.get("branch", "?"),
        },
        "redirector": rd,
        "split_brain": sb,
        "processes": procs,
        "previous_health": previous.get("timestamp", None),
    }

    health_path.write_text(json.dumps(health, indent=2), encoding="utf-8")

    status = "✅" if health["tests_failed"] == 0 else f"⚠ ({health['tests_failed']} failed)"
    print(f"[{now[:19]}] {health['tests_passed']}/{health['tests_total']} tests {status} | trend: {trend} | branch: {health['branch']} | bootstrap: {bs.get('exists', False)}")

    if health["tests_failed"] > 0:
        print(f"  Failed tests:")
        for ft in health["failed_tests"][:5]:
            print(f"    ❌ {ft}")

    if sb.get("count", 0) > 1:
        print(f"  ⚠ Split-brain: {sb['count']} AuthorityLevel definitions")
        for f in sb.get("authority_files", []):
            print(f"    {f}")

    return 0 if health["tests_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

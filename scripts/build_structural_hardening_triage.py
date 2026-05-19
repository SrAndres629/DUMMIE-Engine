#!/usr/bin/env python3
"""Entrypoint wrapper for Structural Hardening Pack 2 triage."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build structural hardening triage reports")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--write-reports", action="store_true")
    parser.add_argument("--max-actions", type=int, default=50)
    parser.add_argument("--include-low-risk", action="store_true")
    parser.add_argument("--fail-on-critical", action="store_true")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    cmd = [
        sys.executable,
        "-m",
        "layers.l2_brain.structural_hardening.cli",
        "--repo-root",
        str(repo_root),
        "--max-actions",
        str(args.max_actions),
    ]

    if args.write_reports:
        cmd.append("--write-reports")
    if args.include_low_risk:
        cmd.append("--include-low-risk")
    if args.fail_on_critical:
        cmd.append("--fail-on-critical")

    completed = subprocess.run(cmd, cwd=repo_root)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())

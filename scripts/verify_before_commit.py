#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import asdict
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from layers.l2_brain.governance.polyglot_verification import (
    build_polyglot_verification_plan,
    evaluate_verification_results,
    parse_git_status_paths,
    run_verification_commands,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run DUMMIE's polyglot verification gate before commit or push."
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="print the required verification plan without running commands",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=None,
        help="override the timeout for each required verification command",
    )
    args = parser.parse_args()

    changed_paths = _git_changed_paths()
    plan = build_polyglot_verification_plan(changed_paths)

    if args.plan_only:
        print(json.dumps(asdict(plan), indent=2, sort_keys=True))
        return 0

    results = run_verification_commands(plan, timeout_seconds=args.timeout_seconds)
    verdict = evaluate_verification_results(plan, results)

    print(json.dumps(asdict(verdict), indent=2, sort_keys=True))
    for result in results:
        if result.exit_code != 0:
            print(f"\nFAILED: {result.command}", file=sys.stderr)
            if result.stdout:
                print(result.stdout, file=sys.stderr)
            if result.stderr:
                print(result.stderr, file=sys.stderr)

    return 0 if verdict.ready_to_commit and verdict.ready_to_push else 1


def _git_changed_paths() -> list[str]:
    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.stderr.strip() or "git status failed")
    return parse_git_status_paths(completed.stdout)


if __name__ == "__main__":
    raise SystemExit(main())

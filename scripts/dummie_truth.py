#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREFERRED_PYTHON = ROOT / ".venv" / "bin" / "python3"
if (
    sys.prefix == sys.base_prefix
    and PREFERRED_PYTHON.exists()
    and Path(sys.executable).resolve() != PREFERRED_PYTHON.resolve()
    and os.environ.get("DUMMIE_TRUTH_NO_REEXEC") != "1"
):
    env = os.environ.copy()
    env["DUMMIE_TRUTH_NO_REEXEC"] = "1"
    os.execve(
        str(PREFERRED_PYTHON), [str(PREFERRED_PYTHON), __file__, *sys.argv[1:]], env
    )

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

L2_ROOT = ROOT / "layers" / "l2_brain"
if str(L2_ROOT) not in sys.path:
    sys.path.insert(0, str(L2_ROOT))

from layers.l2_brain.operational_truth_collectors import collect_truth


def format_text(report) -> str:
    lines = [
        "=== DUMMIE OPERATIONAL TRUTH ===",
        f"Repo: {report.repo_root}",
        f"Summary: {report.summary()}",
    ]
    for check in report.checks:
        evidence = "; ".join(check.evidence) if check.evidence else check.error
        lines.append(f"- [{check.status.value}] {check.layer} {check.name}: {evidence}")
        if check.next_repair:
            lines.append(f"  next: {check.next_repair}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report DUMMIE Engine operational truth."
    )
    parser.add_argument(
        "--json", action="store_true", help="Print machine-readable JSON."
    )
    parser.add_argument(
        "--include-slow",
        action="store_true",
        help="Run slower probes such as model discovery and Kuzu open.",
    )
    args = parser.parse_args()

    report = collect_truth(str(ROOT), include_slow=args.include_slow)
    report_path = ROOT / ".aiwg" / "reports" / "operational_truth.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report.to_dict(), indent=2) + "\n")

    if args.json:
        sys.stdout.write(json.dumps(report.to_dict()) + "\n")
        sys.stdout.flush()
    else:
        sys.stdout.write(format_text(report) + "\n")
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

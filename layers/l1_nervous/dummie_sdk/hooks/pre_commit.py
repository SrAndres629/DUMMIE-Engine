#!/usr/bin/env python3
"""
DUMMIE Engine pre-commit hook.
Runs Architecture Guardian on staged Python files.
"""

import sys
import subprocess
from pathlib import Path


def find_sdk() -> Path:
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        candidate = parent / "layers" / "l1_nervous" / "dummie_sdk"
        if candidate.is_dir():
            return candidate
    return cwd / "dummie_sdk"


def get_staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        capture_output=True,
        text=True,
        cwd=Path.cwd(),
    )
    return [Path(f.strip()) for f in result.stdout.splitlines() if f.strip()]


def main():
    sdk_path = find_sdk()
    sys.path.insert(0, str(sdk_path.parent))
    sys.path.insert(0, str(sdk_path))
    from dummie_sdk.validation import ArchitectureGuardian

    staged = get_staged_files()
    if not staged:
        sys.exit(0)

    root = Path.cwd()
    guardian = ArchitectureGuardian(root=root)
    violations = []
    for file_path in staged:
        full = root / file_path
        if full.exists():
            violations.extend(guardian.scan_file(full))

    exit_code = guardian.enforce(violations)
    if exit_code:
        print(
            "\nCommit blocked by Architecture Guardian. Fix errors above.",
            file=sys.stderr,
        )
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

# Spec: 192_embedding_mesh_foundation
# Spec: DE-V2-L2-192
#!/usr/bin/env python3
"""
Entrypoint wrapper for Semantic Hardening Pack 1.

This wrapper intentionally avoids sys.path mutation by invoking the package module
through `python -m` from repository root.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description="Build DUMMIE semantic hardening index")
    parser.add_argument("--repo-root", default=".", help="Repository root path")
    parser.add_argument("--max-file-bytes", type=int, default=200000, help="Maximum file size to index")
    parser.add_argument("--write-reports", action="store_true", help="Write reports to .aiwg/reports")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    module_args = [
        sys.executable,
        "-m",
        "layers.l2_brain.embedding_mesh.cli",
        "--repo-root",
        str(repo_root),
        "--max-file-bytes",
        str(args.max_file_bytes),
    ]
    if args.write_reports:
        module_args.append("--write-reports")

    completed = subprocess.run(module_args, cwd=repo_root)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())

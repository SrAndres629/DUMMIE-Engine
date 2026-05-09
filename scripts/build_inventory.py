#!/usr/bin/env python3
"""Build a deterministic repository inventory for AIWG indexing."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


DEFAULT_OUTPUT = Path(".aiwg/index/repo_inventory.jsonl")
DEFAULT_FILES_OUTPUT = Path(".aiwg/index/files.txt")
DEFAULT_TREE_OUTPUT = Path(".aiwg/index/repo_tree.md")

IGNORED_PARTS = {
    ".git",
    ".venv",
    ".worktrees",
    "node_modules",
    "__pycache__",
    "dist",
    "target",
    "bin",
    ".pytest_cache",
}

IGNORED_RELATIVE_DIRS = {
    Path(".aiwg/index"),
    Path(".aiwg/events"),
    Path(".aiwg/sessions"),
    Path(".aiwg/cache"),
    Path(".aiwg/runtime"),
    Path(".aiwg/memory"),
    Path(".aiwg/ledger"),
    Path(".aiwg/venv_ssh"),
}

IGNORED_AIWG_DIR_NAMES = {
    "index",
    "events",
    "sessions",
    "cache",
    "runtime",
    "memory",
    "ledger",
    "venv_ssh",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build deterministic AIWG repository inventory artifacts."
    )
    parser.add_argument("--root", default=".", help="repository root to index")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help="JSONL inventory output path",
    )
    parser.add_argument(
        "--files-output",
        default=str(DEFAULT_FILES_OUTPUT),
        help="plain file list output path",
    )
    parser.add_argument(
        "--tree-output",
        default=str(DEFAULT_TREE_OUTPUT),
        help="Markdown tree output path",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="scan and report without writing output files",
    )
    return parser.parse_args()


def normalize_relative(path: Path) -> str:
    return path.as_posix()


def is_ignored_dir(relative_dir: Path) -> bool:
    parts = relative_dir.parts
    if any(part in IGNORED_PARTS for part in parts):
        return True
    for index, part in enumerate(parts[:-1]):
        if part == ".aiwg" and parts[index + 1] in IGNORED_AIWG_DIR_NAMES:
            return True
    return any(relative_dir == ignored for ignored in IGNORED_RELATIVE_DIRS)


def iter_files(root: Path) -> Iterable[Path]:
    for current_root, dirs, files in os.walk(root):
        current = Path(current_root)
        relative_current = current.relative_to(root)

        kept_dirs = []
        for dirname in dirs:
            relative_dir = (
                Path(dirname)
                if relative_current == Path(".")
                else relative_current / dirname
            )
            if not is_ignored_dir(relative_dir):
                kept_dirs.append(dirname)
        dirs[:] = sorted(kept_dirs)

        for filename in sorted(files):
            path = current / filename
            relative_file = path.relative_to(root)
            if path.is_file() and not is_ignored_dir(relative_file.parent):
                yield relative_file


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def guess_layer(relative_path: Path) -> str:
    parts = relative_path.parts
    if len(parts) >= 2 and parts[0] == "layers":
        return parts[1]
    if parts and parts[0].startswith("l") and "_" in parts[0]:
        return parts[0]
    return "root"


def guess_status(relative_path: Path) -> str:
    path_text = normalize_relative(relative_path).lower()
    suffix = relative_path.suffix.lower()
    if "deprecated" in path_text or "legacy" in path_text:
        return "deprecated"
    if (
        "generated" in path_text
        or relative_path.name.endswith(".pb.go")
        or relative_path.name.endswith("_pb2.py")
    ):
        return "generated"
    if suffix in {".proto", ".go", ".py", ".md", ".json", ".yaml", ".yml"}:
        return "active"
    return "unknown"


def build_entries(root: Path) -> list[dict[str, object]]:
    indexed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    entries = []
    for relative_path in iter_files(root):
        full_path = root / relative_path
        stat = full_path.stat()
        entries.append(
            {
                "path": normalize_relative(relative_path),
                "sha256": sha256_file(full_path),
                "size_bytes": stat.st_size,
                "suffix": relative_path.suffix,
                "layer": guess_layer(relative_path),
                "status_guess": guess_status(relative_path),
                "indexed_at": indexed_at,
            }
        )
    return entries


def render_jsonl(entries: Iterable[dict[str, object]]) -> str:
    lines = [
        json.dumps(entry, sort_keys=True, separators=(",", ":"))
        for entry in entries
    ]
    return "\n".join(lines) + ("\n" if lines else "")


def render_files(entries: Iterable[dict[str, object]]) -> str:
    paths = [str(entry["path"]) for entry in entries]
    return "\n".join(paths) + ("\n" if paths else "")


def render_tree(entries: Iterable[dict[str, object]]) -> str:
    paths = [Path(str(entry["path"])) for entry in entries]
    lines = ["# Repository Tree", ""]
    seen_dirs: set[Path] = set()

    for path in paths:
        for depth, parent in enumerate(reversed(path.parents)):
            if parent == Path(".") or parent in seen_dirs:
                continue
            seen_dirs.add(parent)
            lines.append(f"{'  ' * (len(parent.parts) - 1)}- {parent.name}/")
        lines.append(f"{'  ' * (len(path.parts) - 1)}- {path.name}")

    return "\n".join(lines) + "\n"


def resolve_output_path(root: Path, output: str) -> Path:
    path = Path(output)
    if path.is_absolute():
        return path
    return root / path


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Root is not a directory: {root}")

    entries = build_entries(root)
    output = resolve_output_path(root, args.output)
    files_output = resolve_output_path(root, args.files_output)
    tree_output = resolve_output_path(root, args.tree_output)

    if args.dry_run:
        print(f"Would index {len(entries)} files under {root}")
        print(f"Would write JSONL inventory to {output}")
        print(f"Would write file list to {files_output}")
        print(f"Would write repository tree to {tree_output}")
        return 0

    write_text(output, render_jsonl(entries))
    write_text(files_output, render_files(entries))
    write_text(tree_output, render_tree(entries))
    print(f"Indexed {len(entries)} files under {root}")
    print(f"Wrote JSONL inventory to {output}")
    print(f"Wrote file list to {files_output}")
    print(f"Wrote repository tree to {tree_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

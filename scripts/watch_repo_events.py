#!/usr/bin/env python3
"""Deterministic repository file event watcher."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


DEFAULT_SNAPSHOT = ".aiwg/index/file_snapshot.json"
DEFAULT_EVENTS = ".aiwg/events/file_events.jsonl"
IGNORE_DIRS = {
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


@dataclass(frozen=True)
class FileState:
    sha256: str
    size: int | None = None
    mtime_ns: int | None = None

    @classmethod
    def from_snapshot_value(cls, value: Any) -> "FileState | None":
        if isinstance(value, str):
            return cls(sha256=value)
        if not isinstance(value, dict):
            return None
        sha256 = value.get("sha256")
        if not isinstance(sha256, str):
            return None
        size = value.get("size")
        mtime_ns = value.get("mtime_ns")
        return cls(
            sha256=sha256,
            size=size if isinstance(size, int) else None,
            mtime_ns=mtime_ns if isinstance(mtime_ns, int) else None,
        )

    def to_snapshot_value(self) -> dict[str, int | str]:
        value: dict[str, int | str] = {"sha256": self.sha256}
        if self.size is not None:
            value["size"] = self.size
        if self.mtime_ns is not None:
            value["mtime_ns"] = self.mtime_ns
        return value


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scan a repository and emit deterministic file change events.",
    )
    parser.add_argument("--root", default=".", help="repository root to scan")
    parser.add_argument("--snapshot", default=DEFAULT_SNAPSHOT, help="snapshot JSON path")
    parser.add_argument("--events", default=DEFAULT_EVENTS, help="events JSONL path")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--once", action="store_true", help="scan once and exit")
    mode.add_argument("--watch", action="store_true", help="scan repeatedly")
    parser.add_argument("--interval", type=float, default=5.0, help="watch interval in seconds")
    parser.add_argument("--dry-run", action="store_true", help="scan without writing files")
    return parser.parse_args()


def resolve_output_path(root: Path, value: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.resolve()


def relative_posix(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root).as_posix()


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as file_handle:
        for chunk in iter(lambda: file_handle.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def should_descend(directory: Path, root: Path, output_paths: set[Path]) -> bool:
    name = directory.name
    if name in IGNORE_DIRS:
        return False
    if is_relative_to(directory, root / ".aiwg"):
        return False
    if name != ".aiwg":
        return True
    return False


def should_include_file(path: Path, root: Path, output_paths: set[Path]) -> bool:
    if path.resolve() in output_paths:
        return False
    return not is_relative_to(path.resolve(), root / ".aiwg")


def scan(root: Path, output_paths: set[Path]) -> dict[str, FileState]:
    snapshot: dict[str, FileState] = {}
    for current_root, dirs, files in os.walk(root):
        current = Path(current_root)
        dirs[:] = sorted(
            dirname
            for dirname in dirs
            if should_descend((current / dirname).resolve(), root, output_paths)
        )
        for filename in sorted(files):
            path = (current / filename).resolve()
            if not should_include_file(path, root, output_paths):
                continue
            try:
                stat = path.stat()
                snapshot[relative_posix(root, path)] = FileState(
                    sha256=sha256_file(path),
                    size=stat.st_size,
                    mtime_ns=stat.st_mtime_ns,
                )
            except OSError:
                continue
    return snapshot


def load_snapshot(path: Path) -> dict[str, FileState]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as file_handle:
        raw = json.load(file_handle)
    if not isinstance(raw, dict):
        return {}
    snapshot: dict[str, FileState] = {}
    for rel_path, value in raw.items():
        if not isinstance(rel_path, str):
            continue
        state = FileState.from_snapshot_value(value)
        if state is not None:
            snapshot[rel_path] = state
    return snapshot


def write_snapshot(path: Path, snapshot: dict[str, FileState]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {key: snapshot[key].to_snapshot_value() for key in sorted(snapshot)}
    with path.open("w", encoding="utf-8") as file_handle:
        json.dump(payload, file_handle, indent=2, sort_keys=True)
        file_handle.write("\n")


def layer_for_path(path: str) -> str | None:
    parts = path.split("/")
    if len(parts) >= 2 and parts[0] == "layers":
        return parts[1]
    return parts[0] if parts and parts[0] else None


def locus_for_path(path: str) -> dict[str, float]:
    digest = hashlib.sha256(path.encode("utf-8")).digest()
    values = [int.from_bytes(digest[offset : offset + 2], "big") / 65535 for offset in (0, 2, 4)]
    return {"locus_x": values[0], "locus_y": values[1], "locus_z": values[2]}


def event_id_for(event_type: str, path: str, old_sha256: str | None, new_sha256: str | None, lamport_t: int) -> str:
    payload = "\0".join([str(lamport_t), event_type, path, old_sha256 or "", new_sha256 or ""])
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_event(
    event_type: str,
    path: str,
    old_sha256: str | None,
    new_sha256: str | None,
    lamport_t: int,
) -> dict[str, Any]:
    six_d_context: dict[str, Any] = {
        **locus_for_path(path),
        "lamport_t": lamport_t,
        "authority_a": "WATCHER",
        "intent_i": "OBSERVATION",
    }
    return {
        "event_id": event_id_for(event_type, path, old_sha256, new_sha256, lamport_t),
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": event_type,
        "path": path,
        "old_sha256": old_sha256,
        "new_sha256": new_sha256,
        "layer": layer_for_path(path),
        "six_d_context": six_d_context,
    }


def classify_change(old_state: FileState, new_state: FileState) -> str:
    if old_state.sha256 == new_state.sha256:
        raise ValueError("unchanged files cannot be classified as changed")
    if (
        old_state.size is not None
        and old_state.mtime_ns is not None
        and old_state.size == new_state.size
        and old_state.mtime_ns == new_state.mtime_ns
    ):
        return "FILE_HASH_CHANGED"
    return "FILE_MODIFIED"


def diff_snapshots(
    old_snapshot: dict[str, FileState],
    new_snapshot: dict[str, FileState],
    start_lamport: int = 0,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    lamport_t = start_lamport

    for path in sorted(set(new_snapshot) - set(old_snapshot)):
        lamport_t += 1
        events.append(build_event("FILE_ADDED", path, None, new_snapshot[path].sha256, lamport_t))

    for path in sorted(set(old_snapshot) - set(new_snapshot)):
        lamport_t += 1
        events.append(build_event("FILE_DELETED", path, old_snapshot[path].sha256, None, lamport_t))

    for path in sorted(set(old_snapshot) & set(new_snapshot)):
        old_state = old_snapshot[path]
        new_state = new_snapshot[path]
        if old_state.sha256 == new_state.sha256:
            continue
        lamport_t += 1
        event_type = classify_change(old_state, new_state)
        events.append(build_event(event_type, path, old_state.sha256, new_state.sha256, lamport_t))

    return events


def append_events(path: Path, events: list[dict[str, Any]]) -> None:
    if not events:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file_handle:
        for event in events:
            file_handle.write(json.dumps(event, sort_keys=True) + "\n")


def summarize(events: list[dict[str, Any]], dry_run: bool) -> str:
    counts = {
        "FILE_ADDED": 0,
        "FILE_DELETED": 0,
        "FILE_MODIFIED": 0,
        "FILE_HASH_CHANGED": 0,
    }
    for event in events:
        counts[event["event_type"]] += 1
    summary = " ".join(f"{event_type}={counts[event_type]}" for event_type in sorted(counts))
    return f"watch_repo_events dry_run={dry_run} {summary}"


def run_once(root: Path, snapshot_path: Path, events_path: Path, dry_run: bool, start_lamport: int = 0) -> int:
    output_paths = {snapshot_path.resolve(), events_path.resolve()}
    old_snapshot = load_snapshot(snapshot_path)
    new_snapshot = scan(root, output_paths)
    events = diff_snapshots(old_snapshot, new_snapshot, start_lamport=start_lamport)

    if not dry_run:
        append_events(events_path, events)
        write_snapshot(snapshot_path, new_snapshot)

    print(summarize(events, dry_run))
    return start_lamport + len(events)


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    snapshot_path = resolve_output_path(root, args.snapshot)
    events_path = resolve_output_path(root, args.events)

    if args.interval <= 0:
        raise SystemExit("--interval must be greater than 0")

    if args.watch:
        lamport_t = 0
        while True:
            lamport_t = run_once(root, snapshot_path, events_path, args.dry_run, start_lamport=lamport_t)
            time.sleep(args.interval)

    run_once(root, snapshot_path, events_path, args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

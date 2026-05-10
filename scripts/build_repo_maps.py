#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


DEFAULT_INVENTORY = Path(".aiwg/index/repo_inventory.jsonl")
DEFAULT_INDEX_DIR = Path(".aiwg/index")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build AIWG repository maps from inventory JSONL.")
    parser.add_argument("--root", default=".", help="repository root")
    parser.add_argument("--inventory", default=str(DEFAULT_INVENTORY), help="inventory JSONL path")
    parser.add_argument("--index-dir", default=str(DEFAULT_INDEX_DIR), help="AIWG index output directory")
    parser.add_argument("--dry-run", action="store_true", help="report outputs without writing")
    return parser.parse_args()


def load_inventory(path: Path) -> list[dict[str, Any]]:
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entries.append(json.loads(line))
    return entries


def card_name(path: str) -> str:
    safe = path.replace("/", "_").replace("\\", "_").replace(" ", "_")
    return f"{safe}.card.md"


def folder_of(path: str) -> str:
    parent = Path(path).parent.as_posix()
    return "." if parent == "." else parent


def classify_type(path: str, suffix: str) -> str:
    if path.startswith("doc/specs/"):
        return "spec"
    if "/tests/" in path or Path(path).name.startswith("test_"):
        return "test"
    if path.startswith("scripts/"):
        return "script"
    if suffix in {".yaml", ".yml", ".json", ".toml"}:
        return "config"
    if suffix in {".py", ".go", ".ex", ".exs", ".ts", ".tsx", ".js"}:
        return "code"
    return "artifact"


def render_file_card(entry: dict[str, Any]) -> str:
    path = entry["path"]
    file_type = classify_type(path, entry.get("suffix", ""))
    return "\n".join(
        [
            f"# File Card: {path}",
            "",
            "## Identity",
            f"- path: {path}",
            f"- layer: {entry.get('layer', 'unknown')}",
            f"- type: {file_type}",
            f"- status: {entry.get('status_guess', 'unknown')}",
            "- owner_guess: unknown",
            "",
            "## Purpose",
            f"Indexed {file_type} artifact in DUMMIE Engine.",
            "",
            "## Public Contracts",
            "Unknown until deeper static analysis.",
            "",
            "## Dependencies",
            "Unknown.",
            "",
            "## Reverse Dependencies",
            "Unknown.",
            "",
            "## Memory Relevance",
            "Emit file change events and retrieval summaries.",
            "",
            "## Risks",
            "Generated from inventory; verify before using as authoritative evidence.",
            "",
            "## Tests",
            "Unknown.",
            "",
            "## Related Specs",
            "Unknown.",
            "",
            "## Retrieval Summary",
            f"{path} is a {file_type} file in layer {entry.get('layer', 'unknown')}.",
            "",
        ]
    )


def render_folder_card(folder: str, entries: list[dict[str, Any]]) -> str:
    files = "\n".join(f"- {entry['path']}" for entry in entries[:80])
    if len(entries) > 80:
        files += f"\n- ... {len(entries) - 80} more"
    layers = sorted({entry.get("layer", "unknown") for entry in entries})
    return "\n".join(
        [
            f"# Folder Card: {folder}",
            "",
            "## Role",
            f"Contains {len(entries)} indexed files across layers: {', '.join(layers)}.",
            "",
            "## Files",
            files or "- None",
            "",
            "## Active Contracts",
            "Unknown until deeper static analysis.",
            "",
            "## Internal Dependencies",
            "Unknown.",
            "",
            "## External Dependencies",
            "Unknown.",
            "",
            "## Events Produced",
            "FILE_ADDED, FILE_MODIFIED, FILE_DELETED, FILE_HASH_CHANGED.",
            "",
            "## Events Consumed",
            "Inventory and watcher events.",
            "",
            "## Risks",
            "Review unknown/orphan files before execution planning.",
            "",
            "## Missing Tests",
            "Unknown.",
            "",
            "## Related Specs",
            "Unknown.",
            "",
            "## Retrieval Summary",
            f"{folder} contains {len(entries)} files.",
            "",
        ]
    )


def build_graph(entries: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    nodes = []
    folder_nodes = {}
    spec_nodes = []
    edges = []
    for entry in entries:
        path = entry["path"]
        node_type = classify_type(path, entry.get("suffix", ""))
        nodes.append({"id": path, "type": node_type, "layer": entry.get("layer"), "status": entry.get("status_guess")})
        folder = folder_of(path)
        folder_nodes.setdefault(folder, {"id": folder, "type": "folder", "files": 0})
        folder_nodes[folder]["files"] += 1
        edges.append({"from": folder, "to": path, "type": "contains", "confidence": "high"})
        if node_type == "spec":
            spec_nodes.append({"id": path, "type": "spec", "status": entry.get("status_guess")})
            stem = Path(path).stem
            for other in entries:
                other_path = other["path"]
                if other_path != path and stem in other_path:
                    edges.append({"from": path, "to": other_path, "type": "references", "confidence": "low"})
    return (
        {"nodes": nodes, "edges": [edge for edge in edges if edge["type"] == "contains"]},
        {"nodes": list(folder_nodes.values()), "edges": [edge for edge in edges if edge["type"] == "contains"]},
        {"nodes": spec_nodes, "edges": [edge for edge in edges if edge["type"] == "references"]},
        edges,
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    args = parse_args()
    root = Path(args.root).resolve()
    inventory_path = Path(args.inventory)
    if not inventory_path.is_absolute():
        inventory_path = root / inventory_path
    index_dir = Path(args.index_dir)
    if not index_dir.is_absolute():
        index_dir = root / index_dir

    entries = load_inventory(inventory_path)
    by_folder: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for entry in entries:
        by_folder[folder_of(entry["path"])].append(entry)

    layer_counts = Counter(entry.get("layer", "unknown") for entry in entries)
    status_counts = Counter(entry.get("status_guess", "unknown") for entry in entries)
    file_graph, folder_graph, spec_graph, edges = build_graph(entries)

    outputs: dict[Path, str] = {}
    for entry in entries:
        outputs[index_dir / "file_cards" / card_name(entry["path"])] = render_file_card(entry)
    for folder, folder_entries in by_folder.items():
        outputs[index_dir / "folder_cards" / card_name(folder)] = render_folder_card(folder, folder_entries)

    outputs[index_dir / "layer_map.md"] = "# Layer Map\n\n" + "\n".join(
        f"- {layer}: {count}" for layer, count in sorted(layer_counts.items())
    ) + "\n"
    outputs[index_dir / "layer_map.json"] = json.dumps(dict(sorted(layer_counts.items())), indent=2, sort_keys=True) + "\n"
    outputs[index_dir / "hotspot_map.md"] = "# Hotspot Map\n\n" + "\n".join(
        f"- {folder}: {len(folder_entries)} files" for folder, folder_entries in sorted(by_folder.items(), key=lambda item: len(item[1]), reverse=True)[:40]
    ) + "\n"
    outputs[index_dir / "orphan_files.md"] = "# Orphan/Unknown Files\n\n" + "\n".join(
        f"- {entry['path']}" for entry in entries if entry.get("status_guess") == "unknown"
    ) + "\n"
    outputs[index_dir / "generated_files.md"] = "# Generated Files\n\n" + "\n".join(
        f"- {entry['path']}" for entry in entries if entry.get("status_guess") == "generated"
    ) + "\n"
    outputs[index_dir / "deprecated_files.md"] = "# Deprecated Files\n\n" + "\n".join(
        f"- {entry['path']}" for entry in entries if entry.get("status_guess") == "deprecated"
    ) + "\n"
    outputs[index_dir / "file_graph.json"] = json.dumps(file_graph, indent=2, sort_keys=True) + "\n"
    outputs[index_dir / "folder_graph.json"] = json.dumps(folder_graph, indent=2, sort_keys=True) + "\n"
    outputs[index_dir / "spec_graph.json"] = json.dumps(spec_graph, indent=2, sort_keys=True) + "\n"
    outputs[index_dir / "dependency_edges.jsonl"] = "".join(json.dumps(edge, sort_keys=True) + "\n" for edge in edges)

    if args.dry_run:
        print(f"Would build {len(outputs)} map artifacts from {len(entries)} inventory entries")
        print(f"Layer counts: {dict(sorted(layer_counts.items()))}")
        print(f"Status counts: {dict(sorted(status_counts.items()))}")
        return 0

    for path, content in outputs.items():
        write(path, content)
    print(f"Built {len(outputs)} map artifacts from {len(entries)} inventory entries")
    print(f"Wrote maps under {index_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

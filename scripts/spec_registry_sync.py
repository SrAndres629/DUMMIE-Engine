#!/usr/bin/env python3
"""Spec: DE-V2-L2-201 Canonical Spec Binding Registry.

Synchronize canonical spec bindings from `doc/specs/*.md` into one YAML registry.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml


def _parse_frontmatter(text: str, path: Path) -> tuple[dict[str, str], str]:
    match = re.match(r"(?s)^---\n(.*?)\n---\n(.*)$", text)
    if not match:
        raise ValueError(f"{path}: missing or malformed YAML frontmatter")
    front = match.group(1)
    body = match.group(2)
    meta: dict[str, str] = {}
    for raw in front.splitlines():
        m = re.match(r'^([a-zA-Z0-9_]+):\s*"(.*)"\s*$', raw.strip())
        if m:
            meta[m.group(1)] = m.group(2)
    return meta, body


def _parse_physical_evidence(body: str) -> list[str]:
    lines = body.splitlines()
    start = None
    for idx, line in enumerate(lines):
        if line.strip() == "## Physical Evidence":
            start = idx + 1
            break
    if start is None:
        return []

    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        for rel in re.findall(r"`([^`]+)`", line):
            out.append(rel.strip())
    return out


def _classify_paths(paths: list[str]) -> dict[str, list[str]]:
    runtime_files: list[str] = []
    test_files: list[str] = []
    docs_files: list[str] = []
    script_files: list[str] = []
    data_files: list[str] = []

    for rel in paths:
        if rel.startswith(("layers/", "dummie/", "bin/")):
            runtime_files.append(rel)
        if rel.startswith("tests/") or "/tests/" in rel:
            test_files.append(rel)
        if rel.startswith(("doc/", "docs/")):
            docs_files.append(rel)
        if rel.startswith("scripts/"):
            script_files.append(rel)
        if rel.startswith(".aiwg/"):
            data_files.append(rel)

    return {
        "runtime_files": sorted(dict.fromkeys(runtime_files)),
        "test_files": sorted(dict.fromkeys(test_files)),
        "docs_files": sorted(dict.fromkeys(docs_files)),
        "script_files": sorted(dict.fromkeys(script_files)),
        "data_files": sorted(dict.fromkeys(data_files)),
    }


def build_registry(repo_root: Path) -> dict[str, Any]:
    specs_dir = repo_root / "doc" / "specs"
    entries: list[dict[str, Any]] = []
    errors: list[str] = []

    for spec_path in sorted(specs_dir.rglob("*.md")):
        text = spec_path.read_text(encoding="utf-8")
        try:
            meta, body = _parse_frontmatter(text, spec_path)
        except Exception as exc:
            errors.append(str(exc))
            continue

        spec_rel = str(spec_path.relative_to(repo_root))
        feature_rel = spec_rel.replace(".md", ".feature")
        rules_rel = spec_rel.replace(".md", ".rules.json")

        evidence = _parse_physical_evidence(body)
        for rel in evidence:
            if " " in rel:
                continue
            p = repo_root / rel
            if not p.exists():
                errors.append(f"{spec_rel}: missing evidence path `{rel}`")

        classifications = _classify_paths(evidence)
        entries.append(
            {
                "spec_id": meta.get("spec_id", ""),
                "title": meta.get("title", ""),
                "status": meta.get("status", ""),
                "layer": meta.get("layer", ""),
                "last_verified_on": meta.get("last_verified_on", ""),
                "spec_path": spec_rel,
                "feature_path": feature_rel,
                "rules_path": rules_rel,
                "physical_evidence": evidence,
                **classifications,
            }
        )

    entries.sort(key=lambda x: x.get("spec_id", ""))
    return {
        "schema_version": "dummie.spec_binding_registry.v1",
        "generated_from": "doc/specs",
        "spec_count": len(entries),
        "error_count": len(errors),
        "entries": entries,
        "errors": errors,
    }


def write_outputs(repo_root: Path, payload: dict[str, Any]) -> tuple[Path, Path]:
    registry_path = repo_root / ".aiwg" / "spec_registry" / "spec_bindings.yaml"
    report_path = repo_root / ".aiwg" / "reports" / "spec_registry_sync_latest.json"
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    registry_path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    report_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8"
    )
    return registry_path, report_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Sync canonical spec binding registry."
    )
    parser.add_argument("--root", default=".", help="Repository root path.")
    parser.add_argument(
        "--strict", action="store_true", help="Fail if any binding errors are found."
    )
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    payload = build_registry(root)
    registry_path, report_path = write_outputs(root, payload)

    print(f"spec_registry_path={registry_path}")
    print(f"spec_registry_report={report_path}")
    print(
        f"spec_count={payload.get('spec_count', 0)} error_count={payload.get('error_count', 0)}"
    )

    if args.strict and payload.get("error_count", 0) > 0:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())

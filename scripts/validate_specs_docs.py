#!/usr/bin/env python3
"""Validate documentation/spec contracts for consistency and maintainability."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
SPECS_DIR = ROOT / "doc" / "specs"
MCP_GUIDE = ROOT / "doc" / "guides" / "mcp_server_usage.md"
CORE_SPEC = ROOT / "doc" / "CORE_SPEC.md"

ALLOWED_STATUS = {"ACTIVE", "DRAFT", "PROPOSED", "DEPRECATED"}
BOILERPLATE_SENTENCE = "Definir el contrato tecnico minimo de esta capacidad para el sistema actual."
REQUIRED_SECTIONS = [
    "## Purpose",
    "## Current State",
    "## Physical Evidence",
    "## Contract Invariants",
    "## Verification",
    "## Traceability",
]


def parse_frontmatter(text: str, path: Path) -> tuple[dict[str, str], str]:
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


def parse_physical_evidence(body: str) -> list[str]:
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
        for path in re.findall(r"`([^`]+)`", line):
            out.append(path)
    return out


def validate_spec_file(path: Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")

    try:
        meta, body = parse_frontmatter(text, path)
    except ValueError as exc:
        return [str(exc)]

    for key in ("spec_id", "title", "status", "layer", "last_verified_on"):
        if key not in meta or not meta[key]:
            errors.append(f"{path}: missing frontmatter field `{key}`")

    status = meta.get("status", "")
    if status not in ALLOWED_STATUS:
        errors.append(f"{path}: invalid status `{status}` (allowed: {sorted(ALLOWED_STATUS)})")

    if BOILERPLATE_SENTENCE in body:
        errors.append(f"{path}: contains boilerplate sentence")

    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"{path}: missing required section `{section}`")

    sibling_feature = path.with_suffix(".feature")
    sibling_rules = path.with_suffix(".rules.json")
    if not sibling_feature.exists():
        errors.append(f"{path}: missing sibling artifact `{sibling_feature}`")
    if not sibling_rules.exists():
        errors.append(f"{path}: missing sibling artifact `{sibling_rules}`")

    for rel in parse_physical_evidence(body):
        if " " in rel:
            continue
        if rel.startswith("python") or rel.startswith("uv ") or rel.startswith("cd "):
            continue
        target = ROOT / rel
        if not target.exists():
            errors.append(f"{path}: Physical Evidence path does not exist `{rel}`")

    return errors


def validate_core_spec_policy() -> list[str]:
    text = CORE_SPEC.read_text(encoding="utf-8")
    if "Estados permitidos: `ACTIVE`, `DRAFT`, `PROPOSED`, `DEPRECATED`." not in text:
        return [f"{CORE_SPEC}: allowed status policy line changed/missing"]
    return []


def validate_mcp_guide_spec_refs() -> list[str]:
    errors: list[str] = []
    text = MCP_GUIDE.read_text(encoding="utf-8")
    refs = sorted({int(x) for x in re.findall(r"Spec\s+(\d+)", text)})
    spec_files = {p.name for p in SPECS_DIR.glob("*.md")}
    for ref in refs:
        prefix = f"{ref:02d}_"
        if not any(name.startswith(prefix) for name in spec_files):
            errors.append(f"{MCP_GUIDE}: references missing Spec {ref}")
    return errors


def resolve_scope(single_check: str | None) -> list[Path]:
    if single_check:
        path = ROOT / single_check
        if not path.exists():
            raise FileNotFoundError(f"Spec not found: {single_check}")
        return [path]
    return sorted(SPECS_DIR.glob("*.md"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate docs/spec consistency.")
    parser.add_argument("--check", help="Validate only one spec file path (repo-relative).")
    args = parser.parse_args()

    errors: list[str] = []
    try:
        scope = resolve_scope(args.check)
    except FileNotFoundError as exc:
        print(str(exc))
        return 2

    for spec in scope:
        errors.extend(validate_spec_file(spec))

    if not args.check:
        errors.extend(validate_core_spec_policy())
        errors.extend(validate_mcp_guide_spec_refs())

    if errors:
        print("DOC/SPEC VALIDATION FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    print(f"DOC/SPEC VALIDATION OK ({len(scope)} specs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())


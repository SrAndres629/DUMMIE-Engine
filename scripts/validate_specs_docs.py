#!/usr/bin/env python3
# Spec Reference: 201_canonical_spec_binding_registry
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
BOILERPLATE_SENTENCE = (
    "Definir el contrato tecnico minimo de esta capacidad para el sistema actual."
)
REQUIRED_SECTIONS = [
    "## Purpose",
    "## Current State",
    "## Physical Evidence",
    "## Contract Invariants",
    "## Verification",
    "## Traceability",
]

DIRECT_SPEC_RE = re.compile(r"(?im)^\s*(?:#|//|--|;)??\s*Spec Reference:\s*(.+?)\s*$")


def extract_direct_spec_refs(text: str) -> list[str]:
    refs: list[str] = []
    for match in DIRECT_SPEC_RE.finditer(text):
        raw = match.group(1)
        for token in re.split(r"[,\s]+", raw):
            ref = token.strip().strip("`'\"")
            if ref:
                refs.append(ref)
    return refs


def source_has_direct_spec_link(source_path: Path, expected_tokens: set[str]) -> bool:
    try:
        refs = set(
            extract_direct_spec_refs(
                source_path.read_text(encoding="utf-8", errors="ignore")
            )
        )
    except Exception:
        return False
    return bool(refs & expected_tokens)


def spec_direct_tokens(spec_path: Path, meta: dict[str, str]) -> set[str]:
    tokens = {spec_path.stem}
    spec_id = meta.get("spec_id", "")
    if spec_id:
        tokens.add(spec_id)
    return tokens


def build_spec_token_index(repo_root: Path) -> dict[str, str]:
    specs_dir = repo_root / "doc" / "specs"
    token_index: dict[str, str] = {}
    for spec_path in sorted(specs_dir.rglob("*.md")):
        try:
            meta, _ = parse_frontmatter(
                spec_path.read_text(encoding="utf-8"), spec_path
            )
        except Exception:
            continue
        rel = str(spec_path.relative_to(repo_root))
        for token in spec_direct_tokens(spec_path, meta):
            token_index[token] = rel
    return token_index


def _binding_spec_tokens(repo_root: Path, spec_refs: list[str]) -> set[str]:
    tokens: set[str] = set()
    for spec_ref in spec_refs:
        spec_path = repo_root / spec_ref
        if not spec_path.exists():
            continue
        try:
            meta, _ = parse_frontmatter(
                spec_path.read_text(encoding="utf-8"), spec_path
            )
        except Exception:
            continue
        tokens.update(spec_direct_tokens(spec_path, meta))
    return tokens


def build_direct_linkage_report(repo_root: Path) -> dict[str, object]:
    from layers.l2_brain.structural_hardening.bindings import (
        BindingStatus,
        ContractBindingRegistry,
    )

    registry = ContractBindingRegistry()
    spec_token_index = build_spec_token_index(repo_root)
    valid_tokens = set(spec_token_index)
    unlinked: list[str] = []
    invalid_refs: dict[str, list[str]] = {}
    linked_count = 0
    total_count = 0

    for binding in registry._bindings.values():
        if binding.binding_status != BindingStatus.BOUND_ACTIVE_RUNTIME:
            continue
        total_count += 1
        source_path = repo_root / binding.path
        if not source_path.exists() or not source_path.is_file():
            unlinked.append(binding.path)
            continue

        text = source_path.read_text(encoding="utf-8", errors="ignore")
        refs = set(extract_direct_spec_refs(text))
        bad_refs = sorted(ref for ref in refs if ref not in valid_tokens)
        if bad_refs:
            invalid_refs[binding.path] = bad_refs

        expected_tokens = _binding_spec_tokens(repo_root, binding.spec_refs)
        link_tokens = expected_tokens or valid_tokens
        if refs & link_tokens:
            linked_count += 1
        else:
            unlinked.append(binding.path)

    hit_rate = (linked_count / total_count) if total_count else 1.0
    return {
        "bound_active_runtime_count": total_count,
        "direct_spec_linked_count": linked_count,
        "direct_spec_hit_rate": round(hit_rate, 4),
        "unlinked_bound_runtime": sorted(unlinked),
        "invalid_direct_refs": invalid_refs,
    }


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
        errors.append(
            f"{path}: invalid status `{status}` (allowed: {sorted(ALLOWED_STATUS)})"
        )

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
            continue

        if target.is_dir() and target.name not in (
            "docs",
            "specs",
            ".agents",
            "doc",
            "infra",
        ):
            # Enforce pointing to files instead of directories to prevent behavioral linkage bypass
            errors.append(
                f"{path}: Physical Evidence `{rel}` must be a file, not a directory."
            )
            continue

        # Enforce behavioral linkage for source code files
        if (
            target.suffix in (".py", ".go")
            and "tests/" not in rel
            and "tests" not in target.parts
        ):
            try:
                expected_tokens = spec_direct_tokens(path, meta)
                if not source_has_direct_spec_link(target, expected_tokens):
                    expected = ", ".join(sorted(expected_tokens))
                    errors.append(
                        f"{path}: Physical Evidence `{rel}` lacks direct behavioral linkage. One of `{expected}` must be present in a `Spec Reference:` line in the source file."
                    )
            except Exception:
                pass

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
    parser.add_argument(
        "--check", help="Validate only one spec file path (repo-relative)."
    )
    parser.add_argument(
        "--report-direct-linkage",
        action="store_true",
        help="Print BOUND_ACTIVE_RUNTIME direct spec linkage metrics.",
    )
    parser.add_argument(
        "--strict-direct-linkage",
        action="store_true",
        help="Fail when any BOUND_ACTIVE_RUNTIME module lacks direct spec linkage.",
    )
    parser.add_argument(
        "--direct-linkage-only",
        action="store_true",
        help="Run only direct spec linkage checks, ignoring broader docs/spec hygiene.",
    )
    args = parser.parse_args()

    errors: list[str] = []
    scope: list[Path] = []
    if not args.direct_linkage_only:
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

    if args.report_direct_linkage or args.strict_direct_linkage:
        direct_report = build_direct_linkage_report(ROOT)
        print(
            "direct_spec_hit_rate="
            f"{direct_report['direct_spec_hit_rate']} "
            "bound_active_runtime_count="
            f"{direct_report['bound_active_runtime_count']} "
            "direct_spec_linked_count="
            f"{direct_report['direct_spec_linked_count']}"
        )
        unlinked_runtime = direct_report["unlinked_bound_runtime"]
        if (
            args.strict_direct_linkage
            and isinstance(unlinked_runtime, list)
            and unlinked_runtime
        ):
            errors.append(
                "BOUND_ACTIVE_RUNTIME modules missing direct spec linkage: "
                + ", ".join(str(path) for path in unlinked_runtime)
            )

    if errors:
        print("DOC/SPEC VALIDATION FAILED")
        for err in errors:
            print(f"- {err}")
        return 1

    if args.direct_linkage_only:
        print("DIRECT SPEC LINKAGE OK")
    else:
        print(f"DOC/SPEC VALIDATION OK ({len(scope)} specs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

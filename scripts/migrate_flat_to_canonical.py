#!/usr/bin/env python3
"""Automated flat_brain → canonical organ migration tool.

Scans layers/l2_brain/flat_brain/, analyzes imports, determines canonical
destination, copies with import re-writing, and reports migration status.
"""

import ast
import json
import os
import re
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
L2 = REPO_ROOT / "layers" / "l2_brain"
FLAT = L2 / "flat_brain"
SRC = L2 / "src"

CANONICAL_ORGANS: Dict[str, List[str]] = {
    "application": ["use_cases", "ports", "services"],
    "cognition": [],
    "context": [],
    "daemon": [],
    "domain": ["authority", "context", "events", "values"],
    "embedding_mesh": ["cli", "contracts", "providers", "registry"],
    "governance": [],
    "heartbeat": [],
    "infrastructure": ["adapters", "persistence", "gateway"],
    "memory": [],
    "metacognition": [],
    "mission": [],
    "model_mesh": [],
    "proto": [],
    "sdk": [],
    "strategic": [],
    "structural_hardening": ["bindings", "contracts"],
}

IMPORT_ALIASES: Dict[str, str] = {
    "embedding_provider": "model_mesh.embedding_provider",
    "embedding_adapter": "model_mesh.embedding_adapter",
    "embedding_activation_verifier": "model_mesh.embedding_activation_verifier",
    "embedding_memory_router": "model_mesh.embedding_memory_router",
    "model_router": "model_mesh.model_router",
    "model_discovery": "model_mesh.model_discovery",
    "model_executor": "model_mesh.model_executor",
    "neuron_ledger": "model_mesh.neuron_ledger",
    "token_cost_ledger": "model_mesh.token_cost_ledger",
    "event_bus": "infrastructure.event_bus",
    "gateway_contract": "infrastructure.gateway_contract",
    "safe_fallbacks": "infrastructure.safe_fallbacks",
    "cypher_codec": "infrastructure.cypher_codec",
    "auditor_port": "governance.auditor_port",
    "resource_governor": "structural_hardening.resource_governor",
    "metagateway_policy": None,
    "semantic_retrieval": "model_mesh.semantic_retrieval_runtime",
    "socraticode_gateway_adapter": "model_mesh.socraticode_gateway_adapter",
}

IGNORED_MODULES = {
    "__init__",
}


def log(msg: str) -> None:
    print(f"  {msg}")


def resolve_canonical_import(module: str) -> Optional[str]:
    if module in IMPORT_ALIASES:
        return IMPORT_ALIASES[module]
    for organ, subdirs in CANONICAL_ORGANS.items():
        organ_dir = L2 / organ
        mod_path = organ_dir / f"{module}.py"
        if mod_path.exists():
            return f"{organ}.{module}"
        for sub in subdirs:
            sub_path = organ_dir / sub / f"{module}.py"
            if sub_path.exists():
                return f"{organ}.{sub}.{module}"
    return None


def analyze_module(path: Path) -> Dict:
    imports = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({"type": "import", "module": alias.name, "alias": alias.asname})
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append({
                        "type": "importfrom",
                        "module": node.module,
                        "names": [n.name for n in node.names],
                        "level": node.level or 0,
                    })
    except SyntaxError as e:
        return {"error": str(e), "imports": []}
    return {"imports": imports}


def find_canonical_organ(module_name: str) -> Optional[str]:
    scores = {}
    name_lower = module_name.lower()

    organ_keywords = {
        "infrastructure": ["adapter", "kuzu", "db", "persist", "gateway", "event", "bus", "provider", "external", "nervous", "port", "ledger", "codec"],
        "governance": ["auditor", "govern", "policy", "shield", "guard", "compliance", "truth", "kernel", "contract", "scan", "repair"],
        "cognition": ["cogniti", "hook", "reason", "thought", "frame", "bias", "hypothesis", "meta"],
        "context": ["context", "compress", "budget", "packet", "quant", "value", "score", "circulation", "enforcement"],
        "memory": ["memory", "spine", "recall", "retriev", "forget", "stale", "graph", "synaptic"],
        "mission": ["mission", "plan", "orchestrat", "goal", "autonomy", "workbench"],
        "strategic": ["strategic", "advisor", "partner", "coach", "mentor"],
        "daemon": ["daemon", "gateway", "outcome", "diagnostic"],
        "model_mesh": ["model", "router", "executor", "discovery", "embedding", "token", "neuron", "semantic", "mesh"],
        "metacognition": ["metacogn", "deliberat", "pipeline"],
        "embedding_mesh": ["embedding"],
        "sdk": ["sdk", "cli", "client", "api"],
        "heartbeat": ["heartbeat", "pulse", "health", "scheduler"],
        "application": ["usecase", "use_case", "service", "orchestrat"],
        "structural_hardening": ["hardening", "probe", "polyglot", "classif", "resource_govern"],
        "proto": ["proto", "protobuf"],
        "domain": ["domain", "entity", "value_object", "authority"],
    }

    for organ, keywords in organ_keywords.items():
        for kw in keywords:
            if kw in name_lower:
                scores[organ] = scores.get(organ, 0) + 10

    if module_name.startswith("test_"):
        return "tests"

    if scores:
        return max(scores, key=scores.get)

    return "other"


def get_module_names_in_flat_brain() -> List[str]:
    result = []
    for f in sorted(FLAT.iterdir()):
        if f.suffix == ".py" and f.stem not in IGNORED_MODULES:
            result.append(f.stem)
        elif f.is_dir() and (f / "__init__.py").exists():
            result.append(f.name)
    return result


def get_existing_canonical_modules() -> set:
    result = set()
    for organ in CANONICAL_ORGANS:
        organ_dir = L2 / organ
        if not organ_dir.is_dir():
            continue
        for f in organ_dir.iterdir():
            if f.suffix == ".py" and f.stem not in IGNORED_MODULES:
                result.add(f"{organ}.{f.stem}")
            elif f.is_dir():
                for sub in f.iterdir():
                    if sub.suffix == ".py" and sub.stem not in IGNORED_MODULES:
                        result.add(f"{organ}.{f.name}.{sub.stem}")
    return result


def migrate_module(module_name: str, dry_run: bool = True) -> Dict:
    flat_path = FLAT / f"{module_name}.py"
    if not flat_path.exists():
        return {"module": module_name, "status": "NOT_FOUND", "action": None}

    analysis = analyze_module(flat_path)
    organ = find_canonical_organ(module_name)

    dest_dir = L2 / organ if organ != "other" else L2 / "other"
    dest_path = dest_dir / f"{module_name}.py"

    if dest_path.exists():
        return {"module": module_name, "status": "ALREADY_EXISTS", "canonical": f"{organ}.{module_name}", "action": "skip_redundant"}

    content = flat_path.read_text(encoding="utf-8")
    new_content = rewrite_imports(content, module_name)

    action = {
        "module": module_name,
        "source": str(flat_path),
        "destination": str(dest_path),
        "organ": organ,
        "imports": analysis.get("imports", []),
        "needs_rewrite": content != new_content,
        "status": "DRY_RUN" if dry_run else "MIGRATED",
    }

    if not dry_run:
        os.makedirs(str(dest_dir), exist_ok=True)
        if new_content != content:
            dest_path.write_text(new_content, encoding="utf-8")
        else:
            shutil.copy2(str(flat_path), str(dest_path))
        action["status"] = "MIGRATED"

    return action


def rewrite_imports(content: str, module_name: str) -> str:
    lines = content.split("\n")
    result = []
    for line in lines:
        new_line = line
        m = re.match(r"^from\s+(\w+)\s+import", line)
        if m:
            imp = m.group(1)
            canonical = resolve_canonical_import(imp)
            if canonical:
                new_line = line.replace(f"from {imp}", f"from layers.l2_brain.{canonical}", 1)
            elif imp not in {"__future__", "os", "sys", "json", "datetime", "typing", "pathlib", "abc", "enum", "dataclasses", "re", "math", "time", "collections", "functools", "itertools", "uuid", "copy", "inspect", "logging", "warnings", "asyncio", "subprocess", "tempfile", "shutil", "hashlib", "base64", "textwrap", "pprint", "io", "pickle", "threading", "concurrent", "multiprocessing", "http", "urllib", "xml", "configparser", "argparse", "unittest"}:
                new_line = line.replace(f"from {imp}", f"from layers.l2_brain.flat_brain.{imp}", 1)
        elif re.match(r"^import\s+(\w+)", line):
            m2 = re.match(r"^import\s+(\w+)", line)
            if m2:
                imp = m2.group(1)
                if imp not in {"os", "sys", "json", "datetime", "typing", "pathlib", "abc", "enum", "dataclasses", "re", "math", "time", "collections", "functools", "itertools", "uuid", "copy", "inspect", "logging", "warnings"}:
                    canonical = resolve_canonical_import(imp)
                    if canonical:
                        new_line = f"from layers.l2_brain.{canonical} import {imp}"
        result.append(new_line)
    return "\n".join(result)


def scan_for_references(module_name: str) -> List[Dict]:
    """Find all references to this module in the codebase."""
    refs = []
    for root, dirs, files in os.walk(str(REPO_ROOT)):
        dirs[:] = [d for d in dirs if d not in {".venv", "__pycache__", ".git", ".antigravitycli"} and not d.startswith("node_modules")]
        for f in files:
            if not f.endswith(".py"):
                continue
            fp = Path(root) / f
            try:
                text = fp.read_text(encoding="utf-8")
                for pattern in [
                    f"flat_brain.{module_name}",
                    f"from {module_name} import",
                    f"import {module_name}",
                ]:
                    if pattern in text:
                        refs.append({"file": str(fp.relative_to(REPO_ROOT)), "pattern": pattern})
            except (UnicodeDecodeError, OSError):
                continue
    return refs


def update_reference(file_path: str, old_import: str, new_import: str) -> bool:
    full_path = REPO_ROOT / file_path
    if not full_path.exists():
        return False
    content = full_path.read_text(encoding="utf-8")
    if old_import not in content:
        return False
    full_path.write_text(content.replace(old_import, new_import), encoding="utf-8")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Migrate flat_brain modules to canonical organs")
    parser.add_argument("action", choices=["plan", "migrate", "status", "analyze", "references"], default="plan", nargs="?")
    parser.add_argument("--module", "-m", help="Specific module to migrate (omit for all)")
    parser.add_argument("--dry-run", "-n", action="store_true", default=True, help="Dry run (default)")
    parser.add_argument("--no-dry-run", action="store_false", dest="dry_run", help="Actually migrate")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--update-refs", action="store_true", help="Update references after migration")
    args = parser.parse_args()

    if args.action == "status":
        existing = get_existing_canonical_modules()
        modules = get_module_names_in_flat_brain()
        results = []
        for m in modules:
            organ = find_canonical_organ(m)
            dest_dir = L2 / organ if organ != "other" else L2 / "other"
            dest_path = dest_dir / f"{m}.py"
            canonical_ref = f"{organ}.{m}"
            already_canonical = canonical_ref in existing
            results.append({
                "module": m,
                "organ": organ,
                "already_canonical": already_canonical,
                "dest_exists": dest_path.exists(),
                "source_exists": (FLAT / f"{m}.py").exists(),
            })

        migrated = sum(1 for r in results if r["already_canonical"])
        pending = sum(1 for r in results if not r["already_canonical"])
        total = len(results)

        if args.json:
            print(json.dumps({"total": total, "migrated": migrated, "pending": pending, "modules": results}, indent=2))
        else:
            print(f"\n=== flat_brain Migration Status ===\n")
            print(f"  Total modules: {total}")
            print(f"  Already canonical: {migrated}")
            print(f"  Pending migration: {pending}")
            print()
            for r in results:
                status = "✅" if r["already_canonical"] else "⬜"
                print(f"  {status} {r['module']:35s} → {r['organ']}")
        return

    if args.action == "analyze":
        modules = [args.module] if args.module else get_module_names_in_flat_brain()
        results = []
        for m in modules:
            flat_path = FLAT / f"{m}.py"
            if not flat_path.exists():
                print(f"  ⚠ {m}: not found")
                continue
            analysis = analyze_module(flat_path)
            organ = find_canonical_organ(m)
            refs = scan_for_references(m)
            canonical = resolve_canonical_import if m in IMPORT_ALIASES else find_canonical_organ(m)
            results.append({
                "module": m,
                "organ": organ,
                "imports": analysis.get("imports", []),
                "errors": analysis.get("error"),
                "references": refs,
            })

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            for r in results:
                print(f"\n  📦 {r['module']} → {r['organ']}")
                if r["errors"]:
                    print(f"     ❌ {r['errors']}")
                for imp in r.get("imports", []):
                    print(f"     {'📥' if imp['type'] == 'import' else '📤'} {imp['module']}")
                if r["references"]:
                    for ref in r["references"]:
                        print(f"     🔗 {ref['file']}")
        return

    if args.action == "plan":
        modules = [args.module] if args.module else get_module_names_in_flat_brain()
        existing = get_existing_canonical_modules()
        plan = []
        for m in modules:
            organ = find_canonical_organ(m)
            canonical_ref = f"{organ}.{m}"
            if canonical_ref not in existing:
                analysis = analyze_module(FLAT / f"{m}.py") if (FLAT / f"{m}.py").exists() else {"imports": []}
                plan.append({"module": m, "organ": organ, "imports": analysis.get("imports", [])})

        if args.json:
            print(json.dumps({"total_planned": len(plan), "migrations": plan}, indent=2))
        else:
            print(f"\n=== Migration Plan: {len(plan)} modules ===\n")
            for p in plan:
                print(f"  📦 {p['module']:35s} → {p['organ']}")
                for imp in p.get("imports", []):
                    canonical_target = resolve_canonical_import(imp["module"])
                    if canonical_target:
                        print(f"       📤 {imp['module']:30s} → layers.l2_brain.{canonical_target}")
        return

    if args.action == "migrate":
        modules = [args.module] if args.module else get_module_names_in_flat_brain()
        results = []
        for m in modules:
            result = migrate_module(m, dry_run=args.dry_run)
            results.append(result)
            if args.dry_run:
                print(f"  [DRY_RUN] {m:35s} → {result.get('organ', '?'):20s} {result['status']}")
            else:
                print(f"  {'✅' if result['status'] == 'MIGRATED' else '⬜'} {m:35s} → {result.get('organ', '?'):20s} {result['status']}")
                if args.update_refs and result["status"] == "MIGRATED":
                    old_path = f"layers.l2_brain.flat_brain.{m}"
                    new_path = f"layers.l2_brain.{result['organ']}.{m}"
                    refs = scan_for_references(m)
                    for ref in refs:
                        if old_path in ref["pattern"]:
                            if update_reference(ref["file"], old_path, new_path):
                                print(f"       🔗 updated {ref['file']}")

        if args.json:
            print(json.dumps(results, indent=2))
        return


if __name__ == "__main__":
    main()

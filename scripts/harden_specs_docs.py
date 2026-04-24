#!/usr/bin/env python3
"""Bulk-normalize spec markdown docs to an operational contract format."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SPECS_DIR = ROOT / "doc" / "specs"
BOILERPLATE_SENTENCE = "Definir el contrato tecnico minimo de esta capacidad para el sistema actual."

LAYER_EVIDENCE = {
    "L0": "layers/l0_overseer",
    "L1": "layers/l1_nervous",
    "L2": "layers/l2_brain",
    "L3": "layers/l3_shield",
    "L4": "layers/l4_edge",
    "L5": "layers/l5_muscle",
    "L6": "layers/l6_skin",
    "CROSS": "README.md",
    "L0_OVERSEER": "layers/l0_overseer",
}

STATUS_STATE = {
    "ACTIVE": "Capacidad activa con evidencia verificable en el repositorio.",
    "DRAFT": "Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.",
    "PROPOSED": "Diseño de roadmap; implementación parcial o no integrada al flujo principal.",
    "DEPRECATED": "Contrato histórico; no debe usarse para trabajo operativo nuevo.",
}


def parse_frontmatter(text: str) -> tuple[str, dict[str, str], str]:
    match = re.match(r"(?s)^(---\n.*?\n---\n)(.*)$", text)
    if not match:
        raise ValueError("Missing YAML frontmatter")
    front = match.group(1)
    body = match.group(2)
    meta: dict[str, str] = {}
    for raw in front.splitlines():
        m = re.match(r'^([a-zA-Z0-9_]+):\s*"(.*)"\s*$', raw.strip())
        if m:
            meta[m.group(1)] = m.group(2)
    return front, meta, body


def make_body(spec_file: Path, meta: dict[str, str]) -> str:
    title = meta.get("title") or spec_file.stem
    status = meta.get("status", "DRAFT")
    layer = meta.get("layer", "CROSS")
    state_text = STATUS_STATE.get(status, STATUS_STATE["DRAFT"])
    layer_path = LAYER_EVIDENCE.get(layer, "README.md")
    rel_spec = f"doc/specs/{spec_file.name}"
    rel_feature = f"doc/specs/{spec_file.stem}.feature"
    rel_rules = f"doc/specs/{spec_file.stem}.rules.json"

    return f"""# {title}

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
{state_text}

## Physical Evidence
- `{rel_spec}`
- `{rel_feature}`
- `{rel_rules}`
- `{layer_path}`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check {rel_spec}
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check {rel_spec}` |
| Artefactos hermanos presentes | `{rel_feature}` y `{rel_rules}` | `python3 scripts/validate_specs_docs.py --check {rel_spec}` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check {rel_spec}` |
"""


def main() -> int:
    changed = 0
    for spec_file in sorted(SPECS_DIR.glob("*.md")):
        text = spec_file.read_text(encoding="utf-8")
        if BOILERPLATE_SENTENCE not in text:
            continue
        front, meta, _ = parse_frontmatter(text)
        new_text = front + make_body(spec_file, meta)
        spec_file.write_text(new_text, encoding="utf-8")
        changed += 1
    print(f"Normalized specs: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


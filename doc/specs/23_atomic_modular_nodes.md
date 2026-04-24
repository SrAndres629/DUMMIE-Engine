---
spec_id: "DE-V2-L1-23"
title: "Nodos Atómicos y Modularidad Plug & Play"
status: "ACTIVE"
layer: "L1"
last_verified_on: "2026-04-24"
---
# Nodos Atómicos y Modularidad Plug & Play

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad activa con evidencia verificable en el repositorio.

## Physical Evidence
- `doc/specs/23_atomic_modular_nodes.md`
- `doc/specs/23_atomic_modular_nodes.feature`
- `doc/specs/23_atomic_modular_nodes.rules.json`
- `layers/l1_nervous`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/23_atomic_modular_nodes.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/23_atomic_modular_nodes.md` |
| Artefactos hermanos presentes | `doc/specs/23_atomic_modular_nodes.feature` y `doc/specs/23_atomic_modular_nodes.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/23_atomic_modular_nodes.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/23_atomic_modular_nodes.md` |

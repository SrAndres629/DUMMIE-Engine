---
spec_id: "DE-V2-L0-11"
title: "Estructura de Monorepo Soberano"
status: "ACTIVE"
layer: "L0"
last_verified_on: "2026-04-24"
---
# Estructura de Monorepo Soberano

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad activa con evidencia verificable en el repositorio.

## Physical Evidence
- `doc/specs/11_monorepo_structure.md`
- `doc/specs/11_monorepo_structure.feature`
- `doc/specs/11_monorepo_structure.rules.json`
- `layers/l0_overseer`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/11_monorepo_structure.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/11_monorepo_structure.md` |
| Artefactos hermanos presentes | `doc/specs/11_monorepo_structure.feature` y `doc/specs/11_monorepo_structure.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/11_monorepo_structure.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/11_monorepo_structure.md` |

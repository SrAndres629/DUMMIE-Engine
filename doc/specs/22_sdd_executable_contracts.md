---
spec_id: "DE-V2-L3-22"
title: "Contratos Ejecutables de Gobernanza (SDD)"
status: "ACTIVE"
layer: "L3"
last_verified_on: "2026-04-24"
---
# Contratos Ejecutables de Gobernanza (SDD)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad activa con evidencia verificable en el repositorio.

## Physical Evidence
- `doc/specs/22_sdd_executable_contracts.md`
- `doc/specs/22_sdd_executable_contracts.feature`
- `doc/specs/22_sdd_executable_contracts.rules.json`
- `layers/l3_shield`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/22_sdd_executable_contracts.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/22_sdd_executable_contracts.md` |
| Artefactos hermanos presentes | `doc/specs/22_sdd_executable_contracts.feature` y `doc/specs/22_sdd_executable_contracts.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/22_sdd_executable_contracts.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/22_sdd_executable_contracts.md` |

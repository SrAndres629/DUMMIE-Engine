---
spec_id: "DE-V2-L0-05"
title: "Stack de Orquestación y Arbitraje"
status: "DRAFT"
layer: "L0"
last_verified_on: "2026-04-24"
---
# Stack de Orquestación y Arbitraje

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/05_orchestration_stack_and_glue.md`
- `doc/specs/05_orchestration_stack_and_glue.feature`
- `doc/specs/05_orchestration_stack_and_glue.rules.json`
- `layers/l0_overseer/__init__.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/05_orchestration_stack_and_glue.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/05_orchestration_stack_and_glue.md` |
| Artefactos hermanos presentes | `doc/specs/05_orchestration_stack_and_glue.feature` y `doc/specs/05_orchestration_stack_and_glue.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/05_orchestration_stack_and_glue.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/05_orchestration_stack_and_glue.md` |

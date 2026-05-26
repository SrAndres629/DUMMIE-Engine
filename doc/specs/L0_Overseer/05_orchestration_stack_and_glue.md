---
spec_id: DE-V2-L0-05
title: Stack de Orquestación y Arbitraje
status: DRAFT
layer: L0
last_verified_on: '2026-04-24'
version: 1.0.0
namespace: dummie.engine.l0
claims:
- id: 05_orchestration_stack_and_glue-file-valid
  description: Spec file '05_orchestration_stack_and_glue.md' exists, parses valid
    YAML frontmatter, and is not empty.
  verify_cmd: python3 -c "import yaml; d=yaml.safe_load(open('/media/datasets/DUMMIE
    Engine/doc/specs/L0_Overseer/05_orchestration_stack_and_glue.md').read().split('---')[1]);
    assert d, 'empty frontmatter'"
  severity: critical
---
# Stack de Orquestación y Arbitraje

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/L0_Overseer/05_orchestration_stack_and_glue.md`
- `doc/specs/L0_Overseer/05_orchestration_stack_and_glue.feature`
- `doc/specs/L0_Overseer/05_orchestration_stack_and_glue.rules.json`
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

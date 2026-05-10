---
spec_id: "DE-V2-L5-35"
title: "Pipeline de Necro-Learning"
status: "DRAFT"
layer: "L5"
last_verified_on: "2026-04-24"
---
# Pipeline de Necro-Learning

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/35_necro_learning_pipeline.md`
- `doc/specs/35_necro_learning_pipeline.feature`
- `doc/specs/35_necro_learning_pipeline.rules.json`
- `layers/l5_muscle`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/35_necro_learning_pipeline.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/35_necro_learning_pipeline.md` |
| Artefactos hermanos presentes | `doc/specs/35_necro_learning_pipeline.feature` y `doc/specs/35_necro_learning_pipeline.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/35_necro_learning_pipeline.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/35_necro_learning_pipeline.md` |

---
spec_id: "DE-V2-L2-12"
title: "Modelo Formal de Memoria 6D-Context"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-04-24"
---
# Modelo Formal de Memoria 6D-Context

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad activa con evidencia verificable en el repositorio.

## Physical Evidence
- `doc/specs/12_6d_context_model.md`
- `doc/specs/12_6d_context_model.feature`
- `doc/specs/12_6d_context_model.rules.json`
- `layers/l2_brain`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/12_6d_context_model.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/12_6d_context_model.md` |
| Artefactos hermanos presentes | `doc/specs/12_6d_context_model.feature` y `doc/specs/12_6d_context_model.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/12_6d_context_model.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/12_6d_context_model.md` |

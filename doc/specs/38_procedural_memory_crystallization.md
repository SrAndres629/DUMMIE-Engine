---
spec_id: "DE-V2-L2-38"
title: "Cristalización de Memoria Procedimental (Kaizen Loop)"
status: "DRAFT"
layer: "L2"
last_verified_on: "2026-04-24"
---
# Cristalización de Memoria Procedimental (Kaizen Loop)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/38_procedural_memory_crystallization.md`
- `doc/specs/38_procedural_memory_crystallization.feature`
- `doc/specs/38_procedural_memory_crystallization.rules.json`
- `layers/l2_brain/daemon.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/38_procedural_memory_crystallization.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/38_procedural_memory_crystallization.md` |
| Artefactos hermanos presentes | `doc/specs/38_procedural_memory_crystallization.feature` y `doc/specs/38_procedural_memory_crystallization.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/38_procedural_memory_crystallization.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/38_procedural_memory_crystallization.md` |

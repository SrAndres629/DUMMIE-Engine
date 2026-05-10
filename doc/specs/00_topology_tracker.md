---
spec_id: "DE-V2-L0-00"
title: "Rastreador de Topología y Soberanía"
status: "ACTIVE"
layer: "L0"
last_verified_on: "2026-04-24"
---
# Rastreador de Topología y Soberanía

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad activa con evidencia verificable en el repositorio.

## Physical Evidence
- `doc/specs/00_topology_tracker.md`
- `doc/specs/00_topology_tracker.feature`
- `doc/specs/00_topology_tracker.rules.json`
- `layers/l0_overseer`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/00_topology_tracker.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/00_topology_tracker.md` |
| Artefactos hermanos presentes | `doc/specs/00_topology_tracker.feature` y `doc/specs/00_topology_tracker.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/00_topology_tracker.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/00_topology_tracker.md` |

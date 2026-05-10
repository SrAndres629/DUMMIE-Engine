---
spec_id: "DE-V2-L1-11"
title: "Protocolo de Plano de Datos (Apache Arrow Zero-Copy)"
status: "DRAFT"
layer: "L1"
last_verified_on: "2026-04-24"
---
# Protocolo de Plano de Datos (Apache Arrow Zero-Copy)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/11_arrow_data_plane.md`
- `doc/specs/11_arrow_data_plane.feature`
- `doc/specs/11_arrow_data_plane.rules.json`
- `layers/l1_nervous`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/11_arrow_data_plane.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/11_arrow_data_plane.md` |
| Artefactos hermanos presentes | `doc/specs/11_arrow_data_plane.feature` y `doc/specs/11_arrow_data_plane.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/11_arrow_data_plane.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/11_arrow_data_plane.md` |

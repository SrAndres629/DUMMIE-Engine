---
spec_id: "DE-V2-L2-21"
title: "Software Fabrication Engine (SFE)"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-04-24"
---
# Software Fabrication Engine (SFE)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad activa con evidencia verificable en el repositorio.

## Physical Evidence
- `doc/specs/21_software_fabrication_engine.md`
- `doc/specs/21_software_fabrication_engine.feature`
- `doc/specs/21_software_fabrication_engine.rules.json`
- `layers/l2_brain/daemon.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/21_software_fabrication_engine.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/21_software_fabrication_engine.md` |
| Artefactos hermanos presentes | `doc/specs/21_software_fabrication_engine.feature` y `doc/specs/21_software_fabrication_engine.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/21_software_fabrication_engine.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/21_software_fabrication_engine.md` |

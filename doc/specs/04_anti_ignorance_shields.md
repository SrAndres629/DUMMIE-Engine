---
spec_id: "DE-V2-L3-04"
title: "Escudos Anti-Ignorancia (Active Shields)"
status: "DRAFT"
layer: "L3"
last_verified_on: "2026-04-24"
---
# Escudos Anti-Ignorancia (Active Shields)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/04_anti_ignorance_shields.md`
- `doc/specs/04_anti_ignorance_shields.feature`
- `doc/specs/04_anti_ignorance_shields.rules.json`
- `layers/l3_shield/__init__.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/04_anti_ignorance_shields.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/04_anti_ignorance_shields.md` |
| Artefactos hermanos presentes | `doc/specs/04_anti_ignorance_shields.feature` y `doc/specs/04_anti_ignorance_shields.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/04_anti_ignorance_shields.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/04_anti_ignorance_shields.md` |

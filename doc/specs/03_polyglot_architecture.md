---
spec_id: "DE-V2-L0-03"
title: "Arquitectura Políglota de 7 Capas"
status: "DRAFT"
layer: "L0"
last_verified_on: "2026-04-24"
---
# Arquitectura Políglota de 7 Capas

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/03_polyglot_architecture.md`
- `doc/specs/03_polyglot_architecture.feature`
- `doc/specs/03_polyglot_architecture.rules.json`
- `layers/l0_overseer`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/03_polyglot_architecture.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/03_polyglot_architecture.md` |
| Artefactos hermanos presentes | `doc/specs/03_polyglot_architecture.feature` y `doc/specs/03_polyglot_architecture.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/03_polyglot_architecture.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/03_polyglot_architecture.md` |

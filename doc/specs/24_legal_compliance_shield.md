---
spec_id: "DE-V2-L3-24"
title: "Blindaje Legal y Cumplimiento (L-Shield)"
status: "DRAFT"
layer: "L3"
last_verified_on: "2026-04-24"
---
# Blindaje Legal y Cumplimiento (L-Shield)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/24_legal_compliance_shield.md`
- `doc/specs/24_legal_compliance_shield.feature`
- `doc/specs/24_legal_compliance_shield.rules.json`
- `layers/l3_shield/__init__.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/24_legal_compliance_shield.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/24_legal_compliance_shield.md` |
| Artefactos hermanos presentes | `doc/specs/24_legal_compliance_shield.feature` y `doc/specs/24_legal_compliance_shield.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/24_legal_compliance_shield.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/24_legal_compliance_shield.md` |

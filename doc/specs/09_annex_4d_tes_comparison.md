---
spec_id: "DE-V2-L2-09"
title: "Anexo: Autopsia Arquitectónica y Comparativa (4D-TES)"
status: "DRAFT"
layer: "L2"
last_verified_on: "2026-04-24"
---
# Anexo: Autopsia Arquitectónica y Comparativa (4D-TES)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/09_annex_4d_tes_comparison.md`
- `doc/specs/09_annex_4d_tes_comparison.feature`
- `doc/specs/09_annex_4d_tes_comparison.rules.json`
- `layers/l2_brain`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/09_annex_4d_tes_comparison.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/09_annex_4d_tes_comparison.md` |
| Artefactos hermanos presentes | `doc/specs/09_annex_4d_tes_comparison.feature` y `doc/specs/09_annex_4d_tes_comparison.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/09_annex_4d_tes_comparison.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/09_annex_4d_tes_comparison.md` |

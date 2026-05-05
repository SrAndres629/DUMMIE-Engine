---
spec_id: "DE-V2-L2-42"
title: "Ontological Certainty Map"
status: "DRAFT"
layer: "L2"
last_verified_on: "2026-04-24"
---
# Ontological Certainty Map

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/42_ontological_certainty_map.md`
- `doc/specs/42_ontological_certainty_map.feature`
- `doc/specs/42_ontological_certainty_map.rules.json`
- `layers/l2_brain/daemon.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/42_ontological_certainty_map.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/42_ontological_certainty_map.md` |
| Artefactos hermanos presentes | `doc/specs/42_ontological_certainty_map.feature` y `doc/specs/42_ontological_certainty_map.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/42_ontological_certainty_map.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/42_ontological_certainty_map.md` |

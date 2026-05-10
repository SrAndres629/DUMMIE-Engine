---
spec_id: "DE-V2-L2-42B"
title: "Metacognitive Identity"
status: "PROPOSED"
layer: "L2"
last_verified_on: "2026-04-24"
---
# Metacognitive Identity

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Diseño de roadmap; implementación parcial o no integrada al flujo principal.

## Physical Evidence
- `doc/specs/42_metacognitive_identity.md`
- `doc/specs/42_metacognitive_identity.feature`
- `doc/specs/42_metacognitive_identity.rules.json`
- `layers/l2_brain`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/42_metacognitive_identity.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/42_metacognitive_identity.md` |
| Artefactos hermanos presentes | `doc/specs/42_metacognitive_identity.feature` y `doc/specs/42_metacognitive_identity.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/42_metacognitive_identity.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/42_metacognitive_identity.md` |

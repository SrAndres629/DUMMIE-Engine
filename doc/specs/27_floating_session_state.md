---
spec_id: "DE-V2-L2-27B"
title: "Floating Session State"
status: "PROPOSED"
layer: "L2"
last_verified_on: "2026-04-24"
---
# Floating Session State

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Diseño de roadmap; implementación parcial o no integrada al flujo principal.

## Physical Evidence
- `doc/specs/27_floating_session_state.md`
- `doc/specs/27_floating_session_state.feature`
- `doc/specs/27_floating_session_state.rules.json`
- `layers/l2_brain/daemon.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/27_floating_session_state.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/27_floating_session_state.md` |
| Artefactos hermanos presentes | `doc/specs/27_floating_session_state.feature` y `doc/specs/27_floating_session_state.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/27_floating_session_state.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/27_floating_session_state.md` |

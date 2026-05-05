---
spec_id: "DE-V2-L1-44"
title: "Adaptadores de Canal Pervasivos (The Pervasive Gateway)"
status: "DRAFT"
layer: "L1"
last_verified_on: "2026-04-24"
---
# Adaptadores de Canal Pervasivos (The Pervasive Gateway)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/44_pervasive_channel_adapters.md`
- `doc/specs/44_pervasive_channel_adapters.feature`
- `doc/specs/44_pervasive_channel_adapters.rules.json`
- `layers/l1_nervous/__init__.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/44_pervasive_channel_adapters.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/44_pervasive_channel_adapters.md` |
| Artefactos hermanos presentes | `doc/specs/44_pervasive_channel_adapters.feature` y `doc/specs/44_pervasive_channel_adapters.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/44_pervasive_channel_adapters.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/44_pervasive_channel_adapters.md` |

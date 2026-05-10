---
spec_id: "DE-V2-L6-26"
title: "Interfaz Command Canvas (GUI)"
status: "DRAFT"
layer: "L6"
last_verified_on: "2026-04-24"
---
# Interfaz Command Canvas (GUI)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad en transición; requiere consolidación progresiva de contratos y pruebas.

## Physical Evidence
- `doc/specs/26_command_canvas_gui.md`
- `doc/specs/26_command_canvas_gui.feature`
- `doc/specs/26_command_canvas_gui.rules.json`
- `layers/l6_skin/__init__.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/26_command_canvas_gui.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/26_command_canvas_gui.md` |
| Artefactos hermanos presentes | `doc/specs/26_command_canvas_gui.feature` y `doc/specs/26_command_canvas_gui.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/26_command_canvas_gui.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/26_command_canvas_gui.md` |

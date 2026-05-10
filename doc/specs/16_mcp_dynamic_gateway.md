---
spec_id: "DE-V2-L1-16B"
title: "MCP Dynamic Gateway"
status: "ACTIVE"
layer: "L1"
last_verified_on: "2026-04-24"
---
# MCP Dynamic Gateway

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad activa con evidencia verificable en el repositorio.

## Physical Evidence
- `doc/specs/16_mcp_dynamic_gateway.md`
- `doc/specs/16_mcp_dynamic_gateway.feature`
- `doc/specs/16_mcp_dynamic_gateway.rules.json`
- `layers/l1_nervous/__init__.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/16_mcp_dynamic_gateway.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/16_mcp_dynamic_gateway.md` |
| Artefactos hermanos presentes | `doc/specs/16_mcp_dynamic_gateway.feature` y `doc/specs/16_mcp_dynamic_gateway.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/16_mcp_dynamic_gateway.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/16_mcp_dynamic_gateway.md` |

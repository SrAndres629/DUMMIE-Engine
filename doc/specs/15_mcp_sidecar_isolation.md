---
spec_id: "DE-V2-L1-15"
title: "Aislamiento de I/O y Adaptador MCP (Modelo FEI)"
status: "ACTIVE"
layer: "L1"
last_verified_on: "2026-04-24"
---
# Aislamiento de I/O y Adaptador MCP (Modelo FEI)

## Purpose
Definir el contrato operativo de esta capacidad y su relación con el estado físico vigente.

## Current State
Capacidad activa con evidencia verificable en el repositorio.

## Physical Evidence
- `doc/specs/15_mcp_sidecar_isolation.md`
- `doc/specs/15_mcp_sidecar_isolation.feature`
- `doc/specs/15_mcp_sidecar_isolation.rules.json`
- `layers/l1_nervous`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- `status` debe estar dentro del conjunto permitido por `doc/CORE_SPEC.md`.
- Los artefactos hermanos (`.feature`, `.rules.json`) deben existir junto a la spec.
- Toda referencia en `Physical Evidence` debe resolver a una ruta real del repositorio.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/15_mcp_sidecar_isolation.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Estado permitido | `doc/CORE_SPEC.md` + frontmatter de esta spec | `python3 scripts/validate_specs_docs.py --check doc/specs/15_mcp_sidecar_isolation.md` |
| Artefactos hermanos presentes | `doc/specs/15_mcp_sidecar_isolation.feature` y `doc/specs/15_mcp_sidecar_isolation.rules.json` | `python3 scripts/validate_specs_docs.py --check doc/specs/15_mcp_sidecar_isolation.md` |
| Evidencia física existente | sección `Physical Evidence` | `python3 scripts/validate_specs_docs.py --check doc/specs/15_mcp_sidecar_isolation.md` |

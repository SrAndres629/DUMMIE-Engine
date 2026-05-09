---
spec_id: "DE-V2-L0-47"
title: "Path Normalization & Industrial Environment"
status: "ACTIVE"
layer: "L0"
last_verified_on: "2026-04-28"
---
# Path Normalization & Industrial Environment

## Purpose
Definir el contrato mínimo de resolución de rutas y variables de entorno para evitar hardcodes y deriva entre auditorías, L0, L1 y L2.

## Current State
El repositorio ya usa `DUMMIE_ROOT` y `DUMMIE_AIWG` en scripts y componentes críticos, pero aún conviven rutas históricas y contratos documentales parciales. La validación industrial depende de esta normalización para ser reproducible.

## Physical Evidence
- `scripts/full_industrial_audit.sh`
- `scripts/dummie_mcp_doctor.py`
- `layers/l2_brain/adapters.py`
- `layers/l1_nervous/compressive_memory.py`

## Contract Invariants
- **No Hardcoding:** Los componentes no deben introducir rutas absolutas fuera de límites de runtime documentados.
- **Root Resolution:** La resolución del root debe apoyarse en variables o detección estable, no en supuestos implícitos del cwd.
- **Operational Consistency:** Las mismas rutas deben servir para auditoría, tests y runtime.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/47_path_normalization.md
rg -n "kuzu_data|MemoryState|m\\.\\*|rm -f.*kuzu|os\\.remove\\(" layers scripts doc -S
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Variables estándar | `scripts/full_industrial_audit.sh` | Inspección + ejecución del script |
| Root resolution | `layers/l2_brain/adapters.py` | Tests de integración y rutas |
| Evitar hardcodes frágiles | `scripts/dummie_mcp_doctor.py` | `rg` contractual |

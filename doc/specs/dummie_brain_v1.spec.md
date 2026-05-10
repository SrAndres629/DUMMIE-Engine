---
spec_id: "DE-V2-L1-BRAIN"
title: "DUMMIE Brain MCP Specification v1.0"
status: "DRAFT"
layer: "L1"
last_verified_on: "2026-04-28"
---
# DUMMIE Brain MCP Specification v1.0

## Purpose
Definir el contrato documental del gateway `dummie-brain` como interfaz entre L2 y la infraestructura de herramientas/memoria de L1.

## Current State
El documento conserva la intención histórica del gateway, pero su superficie actual convive con otras capas y contratos más recientes. Se mantiene como `DRAFT` hasta que se consolide una correspondencia completa con los tools y contratos activos.

## Physical Evidence
- `layers/l1_nervous/mcp_server.py`
- `layers/l1_nervous/tools.py`
- `doc/guides/mcp_server_usage.md`

## Contract Invariants
- **Purity:** Las herramientas no deben emitir salida fuera del protocolo esperado.
- **Determinism:** Las operaciones persistentes deben conservar metadatos causales.
- **Fencing:** El gateway debe respetar estados de solo lectura/bloqueo del memory plane.
- **Gateway Pattern:** Los agentes deben descubrir capacidades remotas a través del gateway en lugar de hardcodearlas.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/dummie_brain_v1.spec.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Entrada MCP | `layers/l1_nervous/mcp_server.py` | Inspección de bootstrap |
| Surface de tools | `layers/l1_nervous/tools.py` | Tests/inspección de registro |
| Contrato operativo | `doc/guides/mcp_server_usage.md` | Revisión documental |

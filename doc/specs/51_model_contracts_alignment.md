---
spec_id: "DE-V2-CROSS-51"
title: "Model Contracts Alignment"
status: "ACTIVE"
layer: "CROSS"
last_verified_on: "2026-04-29"
---
# Model Contracts Alignment

## Purpose
Definir y alinear los tipos de modelos (`AuthorityLevel`, `IntentType`, `AgentIntent`) entre L1 y L2 para evitar derivas y fallos de deserialización.

## Current State
Implementado en `layers/l2_brain/models.py` y consumido por L1. Esta spec formaliza el contrato SSoT.

## Physical Evidence
- `layers/l2_brain/models.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- **SSoT**: `layers/l2_brain/models.py` es la fuente de verdad única para las estructuras de datos del dominio.
- **Strict Typing**: Todos los payloads inter-capa deben validar contra estos modelos.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/51_model_contracts_alignment.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| SSoT | `layers/l2_brain/models.py` | Inspección de código |
| Strict Typing | `layers/l2_brain/models.py` | Inspección de código |

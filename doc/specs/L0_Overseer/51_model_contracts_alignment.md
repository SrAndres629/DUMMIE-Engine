---
spec_id: DE-V2-CROSS-51
title: Model Contracts Alignment
status: ACTIVE
layer: L0
last_verified_on: '2026-04-29'
version: 1.0.0
namespace: dummie.engine.cross
---
# Model Contracts Alignment

## Purpose
Definir y alinear los tipos de modelos (`AuthorityLevel`, `IntentType`, `AgentIntent`) entre L1 y L2 para evitar derivas y fallos de deserialización.

## Current State
Implementado en `layers/l2_brain/models.py` y consumido por la ruta L1 oficial mediante `layers/l1_nervous/domain/models.py`, que reexporta las mismas clases. Esta spec formaliza el contrato SSoT.

## Physical Evidence
- `layers/l2_brain/models.py`
- `layers/l1_nervous/domain/models.py`
- `layers/l1_nervous/tests/test_model_contract_alignment.py`
- `layers/l2_brain/tests/test_domain_models.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- **SSoT**: `layers/l2_brain/models.py` es la fuente de verdad única para las estructuras de datos del dominio.
- **L1 Bridge**: `layers/l1_nervous/domain/models.py` no debe definir copias de `AuthorityLevel`, `IntentType` ni `AgentIntent`; debe reexportar las clases de L2.
- **Strict Typing**: Todos los payloads inter-capa deben validar contra estos modelos.
- **Legacy Boundary**: definiciones generadas por Protobuf o modelos legacy bajo `layers/l2_brain/src/brain/domain/` no son la fuente de verdad Python para la ruta L1/L2 oficial.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/51_model_contracts_alignment.md
layers/l2_brain/.venv/bin/python -m pytest -q layers/l1_nervous/tests/test_model_contract_alignment.py layers/l2_brain/tests/test_domain_models.py
rg -n "class AuthorityLevel|class IntentType|class AgentIntent" layers -S
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| SSoT | `layers/l2_brain/models.py` | `layers/l2_brain/.venv/bin/python -m pytest -q layers/l1_nervous/tests/test_model_contract_alignment.py` |
| L1 Bridge | `layers/l1_nervous/domain/models.py` | `layers/l2_brain/.venv/bin/python -m pytest -q layers/l1_nervous/tests/test_model_contract_alignment.py` |
| Strict Typing | `layers/l2_brain/models.py` + `layers/l2_brain/tests/test_domain_models.py` | `layers/l2_brain/.venv/bin/python -m pytest -q layers/l2_brain/tests/test_domain_models.py` |
| Duplicate visibility | generated/legacy definitions remain non-canonical | `rg -n "class AuthorityLevel|class IntentType|class AgentIntent" layers -S` |

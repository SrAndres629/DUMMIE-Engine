---
spec_id: "DE-V2-L1-49"
title: "Typed SDK Generation"
status: "ACTIVE"
layer: "L1"
last_verified_on: "2026-04-29"
---
# Typed SDK Generation

## Purpose
Definir el contrato para la generación dinámica de clientes SDK fuertemente tipados a partir de esquemas MCP, reduciendo la carga cognitiva y garantizando la seguridad de tipos.

## Current State
Implementado y operativo. El componente `layers/l1_nervous/sdk_generator.py` lee los servidores MCP configurados y genera clases cliente en `layers/l1_nervous/generated/`.

## Physical Evidence
- `layers/l1_nervous/sdk_generator.py`
- `layers/l1_nervous/generated/everything_sdk.py`
- `scratch/generate_sdks.py`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Contract Invariants
- **Dynamic Generation**: Los SDKs se generan introspeccionando los esquemas JSON de las herramientas MCP.
- **Type Safety**: Los argumentos de las herramientas se mapean a tipos Python estándar/Pydantic.
- **Immutability**: Los archivos generados no deben ser editados manualmente.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/49_typed_sdk_generation.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Generación Dinámica | `layers/l1_nervous/sdk_generator.py` | Ejecución de `scratch/generate_sdks.py` |
| Seguridad de Tipos | `layers/l1_nervous/generated/` | Inspección de archivos generados |
| Inmutabilidad | Comentarios en archivos generados | Inspección manual |

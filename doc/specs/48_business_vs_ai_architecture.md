---
spec_id: "DE-V2-L0-48"
title: "Bifurcación de Arquitectura: Negocio vs IA"
status: "ACTIVE"
layer: "L0"
last_verified_on: "2026-04-28"
---
# Bifurcación de Arquitectura: Negocio vs IA

## Purpose
Garantizar la estabilidad y el determinismo de los sistemas generados para clientes, aislando el comportamiento heurístico del DUMMIE Engine.

## Current State
Estandarización de contratos de salida para la generación de código.

## Physical Evidence
- `doc/adr/001_architectural_bifurcation.md`
- `doc/specs/48_business_vs_ai_architecture.md`

## Contract Invariants
- Todo generador de Use Case debe emitir código alineado con Arquitectura Hexagonal pura.
- Las entidades del dominio de negocio no deben importar librerías de IA.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/48_business_vs_ai_architecture.md
```

## Traceability
| Invariant | Evidence | Verification |
| --- | --- | --- |
| Aislamiento del Dominio | `doc/adr/001_architectural_bifurcation.md` | Inspección estática de código |

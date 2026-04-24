---
spec_id: "DE-V2-L3-22"
title: "Contratos Ejecutables de Gobernanza (SDD)"
status: "ACTIVE"
layer: "L3"
last_verified_on: "2026-04-24"
---

# Contratos Ejecutables de Gobernanza (SDD)

## Purpose
Definir el contrato tecnico minimo de esta capacidad para el sistema actual.

## Current State
Implementacion parcial/operativa presente en el repositorio.

## Physical Evidence
- `layers/l3_shield`
- `layers/l2_brain/daemon.py`

## Gaps
- Falta trazabilidad fina entre contrato y pruebas de conformidad.
- Existen diferencias historicas entre narrativa anterior y estado fisico actual.

## Next Actions
1. Mantener este contrato alineado con el codigo real de su capa.
2. Agregar o ajustar pruebas de conformidad para validar este contrato.
3. Actualizar `doc/CORE_SPEC.md` y `doc/PHYSICAL_MAP.md` cuando cambie el alcance.

## Sibling Artifacts
- `./22_sdd_executable_contracts.feature`
- `./22_sdd_executable_contracts.rules.json`

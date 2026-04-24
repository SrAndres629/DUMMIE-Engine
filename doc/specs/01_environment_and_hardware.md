---
spec_id: "DE-V2-L5-01"
title: "Entorno Físico y Restricciones del Metal"
status: "DRAFT"
layer: "L5"
last_verified_on: "2026-04-24"
---

# Entorno Físico y Restricciones del Metal

## Purpose
Definir el contrato tecnico minimo de esta capacidad para el sistema actual.

## Current State
Implementacion en transicion; requiere consolidacion de contrato.

## Physical Evidence
- `layers/l5_muscle`
- `layers/l1_nervous/tools.py`

## Gaps
- Falta trazabilidad fina entre contrato y pruebas de conformidad.
- Existen diferencias historicas entre narrativa anterior y estado fisico actual.

## Next Actions
1. Mantener este contrato alineado con el codigo real de su capa.
2. Agregar o ajustar pruebas de conformidad para validar este contrato.
3. Actualizar `doc/CORE_SPEC.md` y `doc/PHYSICAL_MAP.md` cuando cambie el alcance.

## Sibling Artifacts
- `./01_environment_and_hardware.feature`
- `./01_environment_and_hardware.rules.json`

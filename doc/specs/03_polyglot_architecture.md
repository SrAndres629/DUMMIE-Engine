---
spec_id: "DE-V2-L0-03"
title: "Arquitectura Políglota de 7 Capas"
status: "DRAFT"
layer: "L0"
last_verified_on: "2026-04-24"
---

# Arquitectura Políglota de 7 Capas

## Purpose
Definir el contrato tecnico minimo de esta capacidad para el sistema actual.

## Current State
Implementacion en transicion; requiere consolidacion de contrato.

## Physical Evidence
- `layers/l0_overseer`
- `doc/CORE_SPEC.md`
- `doc/PHYSICAL_MAP.md`

## Gaps
- Falta trazabilidad fina entre contrato y pruebas de conformidad.
- Existen diferencias historicas entre narrativa anterior y estado fisico actual.

## Next Actions
1. Mantener este contrato alineado con el codigo real de su capa.
2. Agregar o ajustar pruebas de conformidad para validar este contrato.
3. Actualizar `doc/CORE_SPEC.md` y `doc/PHYSICAL_MAP.md` cuando cambie el alcance.

## Sibling Artifacts
- `./03_polyglot_architecture.feature`
- `./03_polyglot_architecture.rules.json`

---
spec_id: "DE-V2-L1-11"
title: "Protocolo de Plano de Datos (Apache Arrow Zero-Copy)"
status: "DRAFT"
layer: "L1"
last_verified_on: "2026-04-24"
---

# Protocolo de Plano de Datos (Apache Arrow Zero-Copy)

## Purpose
Definir el contrato tecnico minimo de esta capacidad para el sistema actual.

## Current State
Implementacion en transicion; requiere consolidacion de contrato.

## Physical Evidence
- `layers/l1_nervous`
- `proto`
- `dummie_agent_config.json`

## Gaps
- Falta trazabilidad fina entre contrato y pruebas de conformidad.
- Existen diferencias historicas entre narrativa anterior y estado fisico actual.

## Next Actions
1. Mantener este contrato alineado con el codigo real de su capa.
2. Agregar o ajustar pruebas de conformidad para validar este contrato.
3. Actualizar `doc/CORE_SPEC.md` y `doc/PHYSICAL_MAP.md` cuando cambie el alcance.

## Sibling Artifacts
- `./11_arrow_data_plane.feature`
- `./11_arrow_data_plane.rules.json`

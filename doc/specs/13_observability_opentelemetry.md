---
spec_id: "DE-V2-L6-13"
title: "Observabilidad Sistémica (OpenTelemetry)"
status: "DRAFT"
layer: "L6"
last_verified_on: "2026-04-24"
---

# Observabilidad Sistémica (OpenTelemetry)

## Purpose
Definir el contrato tecnico minimo de esta capacidad para el sistema actual.

## Current State
Implementacion en transicion; requiere consolidacion de contrato.

## Physical Evidence
- `layers/l6_skin`
- `doc/guides/mcp_server_usage.md`

## Gaps
- Falta trazabilidad fina entre contrato y pruebas de conformidad.
- Existen diferencias historicas entre narrativa anterior y estado fisico actual.

## Next Actions
1. Mantener este contrato alineado con el codigo real de su capa.
2. Agregar o ajustar pruebas de conformidad para validar este contrato.
3. Actualizar `doc/CORE_SPEC.md` y `doc/PHYSICAL_MAP.md` cuando cambie el alcance.

## Sibling Artifacts
- `./13_observability_opentelemetry.feature`
- `./13_observability_opentelemetry.rules.json`

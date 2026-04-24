---
spec_id: "DE-V2-L1-41"
title: "Protocolo de Handshake y Mensajería (The Wire)"
status: "ACTIVE"
layer: "L1"
last_verified_on: "2026-04-24"
---

# Protocolo de Handshake y Mensajería (The Wire)

## Purpose
Definir el contrato tecnico minimo de esta capacidad para el sistema actual.

## Current State
Implementacion parcial/operativa presente en el repositorio.

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
- `./41_layer_handshake_protocol.feature`
- `./41_layer_handshake_protocol.rules.json`

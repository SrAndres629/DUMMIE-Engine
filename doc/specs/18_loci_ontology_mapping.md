---
spec_id: "DE-V2-L4-18"
title: "Palacio de Loci y RBAC Topográfico"
status: "DRAFT"
layer: "L4"
last_verified_on: "2026-04-24"
---

# Palacio de Loci y RBAC Topográfico

## Purpose
Definir el contrato tecnico minimo de esta capacidad para el sistema actual.

## Current State
Implementacion en transicion; requiere consolidacion de contrato.

## Physical Evidence
- `layers/l4_edge`
- `layers/l1_nervous/mcp_proxy.py`

## Gaps
- Falta trazabilidad fina entre contrato y pruebas de conformidad.
- Existen diferencias historicas entre narrativa anterior y estado fisico actual.

## Next Actions
1. Mantener este contrato alineado con el codigo real de su capa.
2. Agregar o ajustar pruebas de conformidad para validar este contrato.
3. Actualizar `doc/CORE_SPEC.md` y `doc/PHYSICAL_MAP.md` cuando cambie el alcance.

## Sibling Artifacts
- `./18_loci_ontology_mapping.feature`
- `./18_loci_ontology_mapping.rules.json`

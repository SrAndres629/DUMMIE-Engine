---
spec_id: "DE-V2-PULSE-HB"
title: "Operational Heartbeat"
status: "DRAFT"
layer: "L0"
last_verified_on: "2026-04-24"
---

# Operational Heartbeat

## Purpose
Definir tareas periodicas de bajo costo para detectar deriva documental y riesgos operativos.

## Current State
Heartbeat definido a nivel de contrato documental (`.feature` y `.rules.json`) con enfoque operativo.

## Physical Evidence
- `doc/03_pulse/HEARTBEAT.feature`
- `doc/03_pulse/HEARTBEAT.rules.json`
- `doc/specs/18_loci_ontology_mapping.md`
- `doc/specs/44_pervasive_channel_adapters.md`

## Gaps
- Falta pipeline automatizado que ejecute heartbeat como job recurrente.
- Falta consolidar salida de heartbeat en un ledger operacional unico.

## Next Actions
1. Definir comando runtime para ejecutar heartbeat en lote.
2. Registrar resultados de cada pulso en artefacto trazable.
3. Integrar heartbeat a validacion pre-cierre de tareas.

## Sibling Artifacts
- `./HEARTBEAT.feature`
- `./HEARTBEAT.rules.json`

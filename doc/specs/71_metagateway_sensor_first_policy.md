---
spec_id: "SPEC-71"
title: "Meta-Gateway Sensor-First Policy"
status: "ACTIVE"
layer: "l2_brain"
governance: "sensor_first"
last_verified_on: "2026-05-11"
---
# SPEC-71: Meta-Gateway Sensor-First Policy

## Purpose
Optimize token consumption and improve agent precision by mandating sensory discovery before direct file reading.

## Contexto
Para optimizar el consumo de tokens y mejorar la precisión del agente, el descubrimiento de conceptos debe realizarse a través de herramientas sensoriales (Socraticode / Semantic Search / Meta-Gateway) antes de recurrir a la lectura directa de archivos.

## Regla de Oro
**SENSOR-FIRST**: Ningún agente debe leer un archivo completo (`cat`, `view_file`) con propósitos de "descubrimiento de conceptos" sin haber intentado primero una búsqueda semántica o descubrimiento vía Gateway.

## Matriz de Decisión

| Propósito | Condición Previa | Decisión |
|-----------|------------------|----------|
| Concept Discovery | Sin intento de Gateway/Semántico | **WARN / BLOCK** |
| Concept Discovery | Con intento previo | **ALLOW** |
| Line Confirmation | Post-Gateway | **ALLOW** |
| Debug / Stacktrace | Ninguna | **ALLOW** |
| Diff Review | Ninguna | **ALLOW** |

## Current State
Implemented in `layers/l2_brain/metagateway_policy.py` and enforced via `layers/l2_brain/sensor_first_guard.py`.

## Physical Evidence
- `layers/l2_brain/metagateway_policy.py`
- `layers/l2_brain/sensor_first_guard.py`
- `layers/l2_brain/metagateway_runtime_meter.py`

## Contract Invariants
- `concept_discovery` requests without `semantic_search_attempted` or `gateway_attempted` must return `WARN` or `BLOCK`.

## Verification
Verified via `layers/l2_brain/tests/test_metagateway_hardening.py`.

## Traceability
Traced via `gateway_first_policy` metadata in Saga transactions.

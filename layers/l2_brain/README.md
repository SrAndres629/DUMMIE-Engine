# L2 Brain

## Purpose
Orquestación cognitiva y coordinación de ejecución entre contrato, auditoría y transporte.

## Current State
- Estructura plana Python en modo bridge.
- Componentes principales: `models.py`, `orchestrator.py`, `daemon.py`, `gateway_contract.py`, `adapters.py`.
- Parte de los tests aún apunta a namespaces legacy (`brain.*`).

## Key Gaps
1. Contratos de modelos desalineados con consumidores de L1.
2. Falta de integración end-to-end robusta para compensación de sagas.

## Next Actions
1. Unificar modelos de contexto/intención entre L1 y L2.
2. Reparar imports de tests a estructura física vigente.
3. Agregar escenarios de validación de fallos y rollback.

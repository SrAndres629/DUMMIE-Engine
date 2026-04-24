# L2 Brain

## Purpose
Orquestación cognitiva y coordinación de ejecución entre contrato, auditoría y transporte.

## Current State
- Estructura plana Python en modo bridge.
- Componentes principales: `models.py`, `orchestrator.py`, `daemon.py`, `gateway_contract.py`, `adapters.py`.
- Daemon con gate jerárquico activo: toda tarea pasa por `master_skill + subskill` antes de ejecutar herramientas.
- `process_request()` expone outcome explícito (`SUCCESS`/`FAILED`) con estado de pasos para observabilidad.
- Suite `layers/l2_brain/tests` alineada al layout actual (`uv run pytest -q tests`).

## Key Gaps
1. Contratos de modelos desalineados con consumidores de L1.
2. Consolidar contratos de estado/outcome del daemon con consumidores de L1/L0.

## Next Actions
1. Unificar modelos de contexto/intención entre L1 y L2.
2. Publicar contrato de resultado de saga en `gateway_contract.py` para consumo externo.
3. Extender pruebas E2E de compensación y ruteo de subskills en DAG complejos.

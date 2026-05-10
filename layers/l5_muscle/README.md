# L5 Muscle

## Purpose
Capa de ejecución física y contención operativa para acciones del sistema.

## Current State
- Driver MCP: `mcp_driver.py`
- Sandbox manager: `manager.py`
- Compactor de memoria: `compactor.py`

## Key Gaps
1. Controles de sandbox aún básicos.
2. Ruta de ejecución carece de contrato fuerte de errores/reintentos.

## Next Actions
1. Definir política de aislamiento verificable.
2. Endurecer manejo de errores en transporte MCP.
3. Añadir pruebas de resiliencia y cleanup.

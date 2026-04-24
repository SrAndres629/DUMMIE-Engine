# L4 Edge

## Purpose
Descubrimiento y observabilidad de capacidades/entorno para alimentar la orquestación.

## Current State
- Descubrimiento MCP en `tool_discovery.py`.
- Observador de archivos en estado inicial (`file_watcher.py`).

## Key Gaps
1. Parser de capacidades depende de formato textual frágil.
2. Watcher no implementa monitoreo continuo real.

## Next Actions
1. Estandarizar formato de inventario de capacidades.
2. Implementar watcher con backend real y pruebas.
3. Integrar eventos de edge al flujo de orquestación L2.

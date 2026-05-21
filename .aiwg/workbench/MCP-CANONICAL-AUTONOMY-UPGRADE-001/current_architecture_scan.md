# Current Architecture Scan - MCP-CANONICAL-AUTONOMY-UPGRADE-001

## Contexto de la Misión
DUMMIE-Engine se encuentra en un estado de refactorización profunda de la capa `l2_brain`. Se observa una migración de un modelo "flat" hacia uno estructurado (governance, mission, context, memory).

## Puntos de Integración Detectados
- **Gateway MCP:** `dummie_gateway_config.json` (Raíz) y `layers/l1_nervous/mcp_server.py`.
- **Daemon:** `dummie/daemon.py` (Gestión de sesiones/neuronas).
- **Runtime:** `dummie/runtime_chat.py` (Enrutamiento de herramientas).
- **Skills:** Repartidos en `.agents/skills`, `skills/` y `.opencode/skills`.
- **Memoria:** `.aiwg/memory/loci.db` (Kuzu/4D-TES).

## Riesgos Inmediatos
1. Desalineación entre los MCPs recién agregados y la nueva estructura de gobernanza en `l2_brain`.
2. Duplicidad de lógica entre "skills" locales y servidores MCP externos.
3. Desbalance de costos (tokens) por uso ineficiente de herramientas de pensamiento secuencial vs comandos directos.

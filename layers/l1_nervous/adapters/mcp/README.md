# DUMMIE Brain MCP Adapter (L1 Nervous Layer)

Este servidor actúa como la interfaz física entre el LLM (Gemini/Claude) y el núcleo cognitivo del **DUMMIE Engine**. Implementa el estándar **Model Context Protocol (MCP)** para proporcionar un acceso determinista a la memoria y herramientas de fabricación.

## Características (Spec 15 - v2.3.0)
- **Zero Logic Policy:** Actúa puramente como un adaptador de transporte, delegando la lógica al Cerebro (L2).
- **Master/Reader Arbitrage:** Gestión automática de bloqueos de I/O para multi-tenancy.
- **Causal Pruning (Spec 40B):** Optimización de tokens mediante la poda del timeline de memoria.
- **Knowledge Capture (Spec 48/49):** Herramientas integradas para registro de lecciones y ambigüedades.

## Configuración
El servidor requiere un entorno virtual con las dependencias de L2 Brain:
1. Asegúrese de que `uv` está instalado.
2. Ejecute `./mcp_wrapper.sh` para inicializar el entorno y lanzar el servidor.

## Documentación Adicional
- **Guía de Uso:** Consulte [mcp_server_usage.md](../../../doc/guides/mcp_server_usage.md) para ejemplos de conexión y lista de herramientas.
- **Especificación Técnica:** [15_mcp_sidecar_isolation.md](../../../doc/specs/L1_Nervous/15_mcp_sidecar_isolation.md).

## Variables de Entorno
- `DUMMIE_ROOT_DIR`: Directorio raíz del proyecto.
- `DUMMIE_KUZU_DB_PATH`: Ruta al 4D-TES (`.aiwg/memory/loci.db`).

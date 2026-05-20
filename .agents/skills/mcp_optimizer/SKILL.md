# MCP-LLM Efficiency & High-Signal Protocol

Este skill optimiza la interacción entre Gemini CLI y las herramientas MCP para agentes programadores.

## 1. Protocolo de "High-Signal"
Para maximizar el valor técnico y minimizar el ruido cognitivo (tokens), el agente debe seguir estas reglas:

- **Surgical Tooling:** Nunca leas archivos completos si puedes usar `grep_search` con contexto.
- **Batching:** Agrupa las llamadas a herramientas que sean independientes en un solo turno.
- **Structured Reasoning:** Utiliza `mcp_sequentialthinking_sequentialthinking` antes de realizar cambios estructurales profundos.
- **Verification First:** Toda salida del LLM debe ser verificada físicamente antes de ser reportada como exitosa.

## 2. Optimización de Contexto (Context Preservation)
- **Token Budgeting:** Si un archivo es >2000 líneas, usa `read_file` con `start_line` y `end_line`.
- **Artifact Isolation:** No incluyas código de librerías externas o `.venv` en el contexto de razonamiento.
- **Memory Offloading:** Usa `save_memory` con scope `project` para persistir decisiones arquitectónicas complejas y evitar re-investigar.

## 3. Integración con Genkit & Arize
- Para flujos de razonamiento complejos, utiliza `mcp_genkit-mcp-server_run_flow`.
- Toda traza de ejecución debe ser consultada vía `mcp_arize-tracing-assistant` para detectar cuellos de botella en la lógica del agente.

## 4. Estándar de Respuesta para Programadores
- **Concisión:** Máximo 3 líneas de texto explicativo por turno.
- **Rationale:** Explica el *porqué* arquitectónico antes del *qué*.
- **Validation:** Adjunta siempre el resultado de los tests o el estado de git tras la operación.

# Spec L1-16: MCP Dynamic Gateway (Semantic Tool Orchestration) - v2.0

## 1. Contexto y Propósito (Metacognición 2026)
El escalado de capacidades en DUMMIE Engine ha superado el modelo de "carga estática". Esta especificación define el **Gateway Cognitivo**, que no solo actúa como proxy, sino como un **Filtro de Atención** para el LLM, resolviendo la entropía informacional y los conflictos de concurrencia en entornos multi-agente.

## 2. Contrato de Interfaz (Gateway Tools)

### 2.1 `list_remote_servers`
- **Propósito:** Descubrimiento de infraestructuras.
- **Metacognición:** Permite al agente mapear el "mapa de habilidades" del sistema sin saturar su RAM cognitiva.

### 2.2 `list_remote_tools(server_name)`
- **Propósito:** Introspección bajo demanda.

### 2.3 `exec_remote_tool(server_name, tool_name, arguments)`
- **Propósito:** Ejecución de canal único.
- **Tracing:** Cada ejecución genera automáticamente un `CausalID` (Spec 02) que vincula la acción al `Locus` del agente.

### 2.4 `search_capabilities(query)`
- **Propósito:** Descubrimiento semántico.
- **Mecánica:** Integración con KùzuDB para buscar herramientas basadas en resultados de tareas previas similares.

## 3. Resolución de Problemas Reales (Simulation-Driven)

| Problema Identificado | Causalidad | Solución Metacognitiva (2026) |
| :--- | :--- | :--- |
| **Latencia de Round-Trip** | Múltiples saltos entre procesos. | **Intent-Based Pre-fetching:** El Gateway arranca servidores MCP en paralelo cuando detecta un `AgentIntent` complejo antes de que se solicite la tool. |
| **Deriva de Estado** | Un agente modifica archivos y otro no se entera. | **Stateful Proxying:** El Gateway mantiene un "Diff-Cache" de los cambios realizados por herramientas remotas para inyectar avisos de consistencia. |
| **Discovery Exhaustion** | El agente se pierde entre 500+ herramientas posibles. | **Hierarchical Menus:** Las herramientas se agrupan por `Locus` (sw.impl, sw.spec, etc.). Solo se muestran las del Locus activo. |
| **Alucinación de Schema** | El LLM confunde argumentos entre herramientas similares. | **Schema Homogenization:** El Gateway valida los argumentos contra el `Zod/JSON Schema` original antes de enviarlos al sub-proceso. |

## 4. Orquestación Multi-Agente (Swarm Mode)
- **Shared Lock Registry:** El Gateway consulta el `L1_Nervous_Ledger` antes de ejecutar una tool que afecte el sistema de archivos o la memoria, evitando colisiones entre agentes paralelos.
- **Context Injection API:** El Gateway puede inyectar "pistas" en el prompt del LLM sobre herramientas recomendadas basadas en el éxito de otros agentes del enjambre.

## 5. Causalidad y Performance
- **Token Budgeting:** Límite estricto de 2000 tokens para definiciones de herramientas por turno.
- **Latency Budget:** Máximo 50ms de overhead en el routing de paquetes JSON-RPC.
- **Persistence:** Todas las llamadas fallidas se registran como `lessons.jsonl` (Spec 48) para el auto-ajuste del Gateway.

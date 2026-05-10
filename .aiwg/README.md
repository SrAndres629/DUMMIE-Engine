# .aiwg (Active Intelligence Working Group) - Memoria Agéntica Colectiva

## 1. Propósito
Este directorio constituye la **Capa de Memoria Semántica y Persistente** del DUMMIE Engine. Mientras que el motor 4D-TES (KùzuDB) maneja la memoria inmutable de eventos, `.aiwg` almacena la **Cristalización de Conocimiento** (Spec 48) en formatos legibles por humanos y máquinas (JSONL/Markdown).

## 2. Estructura de Memoria (`/memory`)
- **`resolutions.jsonl` (Spec 34):** Registro de decisiones arquitectónicas y compromisos tomados.
- **`lessons.jsonl` (Spec 48):** Lecciones aprendidas de fallos, errores de tooling y correcciones.
- **`ambiguities.jsonl` (Spec 48):** Deuda técnica y "Runtime Commitments" identificados.
- **`ego_state.jsonl` (Spec 36):** El "Stream of Consciousness" de la sesión actual.
- **`ontological_map.json` (Spec 42):** Estado de certeza y "Terra Incognita" del sistema.

## 3. Integración con DUMMIE Memory
El motor **4D-TES** actúa como el "Lóbulo Temporal" (eventos crudos), mientras que `.aiwg` es la "Corteza Prefrontal" (conocimiento destilado).

### Protocolo de Sincronización
1.  **Entrada**: Un `AgentIntent` es procesado por el `CognitiveOrchestrator`.
2.  **Ejecución**: El cambio se persiste en el Merkle-DAG (KùzuDB).
3.  **Crystallization**: Al finalizar, el agente **Kaizen** (sw.qa.poka_yoke) analiza el resultado y actualiza automáticamente los archivos en `.aiwg/memory/`.

## 4. Uso en Tiempo Real
Este directorio DEBE ser monitoreado por cualquier agente que se conecte al motor mediante **MCP**. Al leer `.aiwg`, un agente nuevo adquiere instantáneamente el contexto histórico, la personalidad del proyecto y las lecciones aprendidas por sus predecesores, eliminando la amnesia operativa.

---
**Soberanía:** Este directorio es inmutable para procesos externos; solo los agentes autorizados del swarm pueden realizar mutaciones mediante el `CrystallizationUseCase`.

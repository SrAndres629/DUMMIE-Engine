# DUMMIE MCP Server - Usage Guide

Este servidor actúa como el adaptador universal (USB-C) del **DUMMIE Engine**, permitiendo que agentes externos (Gemini, Claude, GPT) interactúen con la memoria soberana y el núcleo cognitivo (L2 Brain).

## 1. Conexión
El servidor oficial se lanza directamente desde `layers/l1_nervous/mcp_server.py`. En entornos como **Claude Desktop**, configure el servidor con el siguiente comando:

```json
{
  "mcpServers": {
    "dummie-brain": {
      "command": "/home/jorand/Escritorio/DUMMIE Engine/layers/l2_brain/.venv/bin/python",
      "args": ["/home/jorand/Escritorio/DUMMIE Engine/layers/l1_nervous/mcp_server.py"]
    }
  }
}
```

## 2. Herramientas Disponibles (Tools)

| Herramienta | Función | Spec Ref |
| :--- | :--- | :--- |
| `brain_ping` | Diagnóstico de latencia y estado básico. | Legacy 15 |
| `calibrate_neural_links` | Verifica la integridad de KùzuDB y el Ledger. | Legacy 15 |
| `metacognitive_status` | Reporta el estado de certidumbre y modo de operación. | Legacy 42 |
| `read_spec` | Recupera el contrato formal de cualquier Spec. | SDD |
| `ssh_grep` | Búsqueda ultra-rápida vía SSH bridge (Baja Entropía). | Legacy 41 |
| `crystallize` | Persistencia mandataria de conocimiento en el 4D-TES. | Legacy 02 |
| `log_lesson` | Captura fallos y genera lecciones aprendidas. | Legacy 35 |
| `resolve_ambiguity` | Documenta compromisos técnicos y planes de cierre. | Legacy 07 |
| `semantic_recall` | Recupera candidatos desde MCP, conocimiento y 4D-TES para una tarea. | Legacy 44 |
| `tool_card_resolver` | Normaliza schemas, riesgos y textos indexables de herramientas MCP. | Legacy 44 |
| `reasoned_rerank` | Reordena candidatos con razonamiento local en modo sombra. | Legacy 44 |
| `context_shaper` | Produce paquetes compactos para agentes de nube. | Legacy 44 |
| `selection_feedback` | Persiste feedback estructurado de seleccion en 4D-TES. | Legacy 44 |

## 3. Recursos (Resources)

- **`brain://identity`**: Información sobre el arquetipo y axiomas del sistema.
- **`memory://timeline`**: Historial causal (Merkle-DAG). Nota: Aplica **Causal Pruning** (últimos 50 nodos).
- **`memory://loci`**: Topología actual del grafo ontológico.
- **`memory://decisions`**: Últimas 10 decisiones registradas en el Ledger.
- **`specs://active`**: Índice de especificaciones técnicas cargadas.

## 4. Modos de Operación (Resiliencia)
El servidor implementa el protocolo de arbitraje legacy:
- **MASTER**: Acceso total (lectura/escritura).
- **READER**: Acceso degradado (Solo Lectura). Se activa automáticamente si la base de datos está bloqueada por otro proceso. Las herramientas de mutación (`crystallize`, `log_lesson`) devolverán el error `ERR_MEMORY_LOCKED`.

## 5. Mejores Prácticas
1. **Always Read Specs**: Antes de modificar código, use `read_spec` para entender el contrato.
2. **Crystallize Daily**: No termine una tarea sin cristalizar el conocimiento.
3. **Log Lessons**: Si un comando falla, use `log_lesson` para que el sistema aprenda y no repita el error.

## 6. Legacy Reference Mapping
Las siguientes referencias de especificaciones encontradas en esta guía pertenecen a la arquitectura histórica del sistema y no son canónicas en el **Plan V1**. Se mantienen por trazabilidad documental pero se consideran no bloqueantes para validación:

| Legacy Identifier | Canonical Equivalent / Status |
| :--- | :--- |
| S02 | Implemented in layers/l1_nervous/compressive_memory.py |
| S07 | Legacy. Replaced by Mission Coherence Guard. |
| S15 | Implemented in layers/l1_nervous/repo_guard.py |
| S35 | Legacy. Lessons are now part of Technical Debt Intelligence. |
| S41 | Implemented in layers/l4_ext/shannon_entropy_mock.py |
| S42 | Implemented in layers/l2_brain/state_coherence_guard.py |
| S44 | Implemented in layers/l2_brain/local_context_compressor.py |

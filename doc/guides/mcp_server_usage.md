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
| `brain_ping` | Diagnóstico de latencia y estado básico. | Spec 15 |
| `calibrate_neural_links` | Verifica la integridad de KùzuDB y el Ledger. | Spec 15 |
| `metacognitive_status` | Reporta el estado de certidumbre y modo de operación. | Spec 42 |
| `read_spec` | Recupera el contrato formal de cualquier Spec. | SDD |
| `ssh_grep` | Búsqueda ultra-rápida vía SSH bridge (Baja Entropía). | Spec 41 |
| `crystallize` | Persistencia mandataria de conocimiento en el 4D-TES. | Spec 02 |
| `log_lesson` | Captura fallos y genera lecciones aprendidas. | Spec 35 |
| `resolve_ambiguity` | Documenta compromisos técnicos y planes de cierre. | Spec 07 |
| `semantic_recall` | Recupera candidatos desde MCP, conocimiento y 4D-TES para una tarea. | Spec 44 |
| `tool_card_resolver` | Normaliza schemas, riesgos y textos indexables de herramientas MCP. | Spec 44 |
| `reasoned_rerank` | Reordena candidatos con razonamiento local en modo sombra. | Spec 44 |
| `context_shaper` | Produce paquetes compactos para agentes de nube. | Spec 44 |
| `selection_feedback` | Persiste feedback estructurado de seleccion en 4D-TES. | Spec 44 |

## 3. Recursos (Resources)

- **`brain://identity`**: Información sobre el arquetipo y axiomas del sistema.
- **`memory://timeline`**: Historial causal (Merkle-DAG). Nota: Aplica **Causal Pruning** (últimos 50 nodos).
- **`memory://loci`**: Topología actual del grafo ontológico.
- **`memory://decisions`**: Últimas 10 decisiones registradas en el Ledger.
- **`specs://active`**: Índice de especificaciones técnicas cargadas.

## 4. Modos de Operación (Resiliencia)
El servidor implementa el protocolo de arbitraje de la **Spec 15**:
- **MASTER**: Acceso total (lectura/escritura).
- **READER**: Acceso degradado (Solo Lectura). Se activa automáticamente si la base de datos está bloqueada por otro proceso. Las herramientas de mutación (`crystallize`, `log_lesson`) devolverán el error `ERR_MEMORY_LOCKED`.

## 5. Mejores Prácticas
1. **Always Read Specs**: Antes de modificar código, use `read_spec` para entender el contrato.
2. **Crystallize Daily**: No termine una tarea sin cristalizar el conocimiento.
3. **Log Lessons**: Si un comando falla, use `log_lesson` para que el sistema aprenda y no repita el error.

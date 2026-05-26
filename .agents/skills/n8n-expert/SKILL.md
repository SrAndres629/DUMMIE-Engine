---
name: n8n Expert Operations
description: Guia operativa para analizar, disenar, depurar, administrar y optimizar automatizaciones n8n desde DUMMIE.
version: 1.0.0
---

# n8n Expert

Usa este skill cuando el objetivo real sea trabajar con `n8n` como un operador experto desde DUMMIE y OpenCode.

## Objetivo

Convertir lenguaje natural en operaciones concretas sobre `n8n` con el menor costo cognitivo posible:

- descubrir que MCP n8n conviene usar
- analizar nodos, templates y workflows
- validar y depurar workflows
- administrar ejecuciones, credenciales y tablas de datos
- documentar riesgos antes de tocar produccion

## Seleccion de servidor MCP

1. Usa `n8n.*` para documentacion de nodos, templates, validacion general y operaciones de workflow en la instancia local.
2. Usa `n8n_api.*` cuando necesites cobertura amplia del API de n8n, especialmente `Data Tables`, tags, variables, proyectos o usuarios.
3. Usa `n8n_lint.*` cuando necesites generar workflows desde texto, comparar versiones, explicar ejecuciones fallidas o aplicar chequeos de calidad antes de desplegar.

## Flujo recomendado

1. Descubrir capacidades con `dummie_discover_capabilities(query="n8n")`.
2. Analizar el target exacto con `dummie_analyze_capability(target=...)`.
3. Ejecutar con `dummie_execute_capability(target=..., arguments=...)`.
4. Para cambios de workflow, validar antes y despues.
5. Si el cambio afecta produccion, registrar limites, dependencias y rollback.

## Heuristicas

- Si el usuario pide "crear" o "modificar" un workflow, empieza por `n8n_lint.workflow.generate` o por templates en `n8n.search_templates`, no por JSON manual.
- Si el usuario pide diagnosticar una falla, prioriza `n8n_lint.execution.explain` o `n8n_lint.execution.timeline`.
- Si el usuario pide administrar recursos globales, prioriza `n8n_api.*`.
- Si el usuario pide comprender nodos o mejores practicas, prioriza `n8n.tools_documentation`, `n8n.search_nodes` y `n8n.get_node`.

## Guardrails

- No editar directamente workflows de produccion sin validar el impacto.
- Preferir modo de solo lectura o diagnostico cuando el objetivo sea investigacion.
- Si una operacion requiere credenciales nuevas, explicitarlo antes de crear recursos.
- Si la tarea depende de un webhook o integracion externa, confirmar URLs, auth y entorno.

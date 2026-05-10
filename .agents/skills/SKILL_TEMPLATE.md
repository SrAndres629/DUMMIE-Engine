---
skill_id: "sw.architect.ddd_pattern_orchestrator"
version: "1.0.0"
description: "Habilidad base para la orquestación de patrones DDD en arquitectura hexagonal."
author: "DUMMIE Engine-SFE"
capabilities:
  - "bounded_context_mapping"
  - "entity_definition"
  - "value_object_validation"
requirements:
  layers: ["L2", "L4"]
  tools: ["kuzu-query", "markdown-parser"]
  dependencies: []
invariants:
  - "purity_of_domain: true"
  - "no_infrastructure_leaks: true"
---

# Skill: DDD Pattern Orchestrator

Esta habilidad permite al agente arquitecto mapear ideas a estructuras de dominio puras.

## Protocolo de Ejecución
1. Ingesta de Idea Inicial.
2. Identificación de Agregados.
3. Emisión de Spec Proto (LST).

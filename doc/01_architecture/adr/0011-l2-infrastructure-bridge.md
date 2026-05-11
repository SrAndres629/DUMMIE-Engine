---
spec_id: "DE-V2-[ADR-011](0011-l2-infrastructure-bridge.md)"
title: "Bootstrap de Memoria vía L2-Python Bridge"
status: "ACTIVE"
version: "1.1.0"
layer: "L0"
namespace: "io.dummie.v2.adr"
authority: "ARCHITECT"
tags: ["architectural_decision", "bootstrap", "kuzudb", "l2_brain"]
---

# [ADR-011](0011-l2-infrastructure-bridge.md): Bootstrap de Memoria vía L2-Python Bridge

## Abstract
La Capa L4 (Zig) aún no posee los bindings estables de KùzuDB necesarios para el Palacio de Loci. Sin embargo, el desarrollo del proyecto requiere persistencia causal inmediata para evitar la pérdida de contexto histórico. Esta decisión autoriza temporalmente a la Capa L2 (Brain) a gestionar el archivo de base de datos `.aiwg/memory/loci.db` utilizando la librería nativa de Python.

## 1. Cognitive Context Model (Ref)
Para los invariantes de aislamiento de infraestructura, los parámetros de la base de datos temporal y las reglas de migración futura, consulte el archivo hermano [0011-l2-infrastructure-bridge.rules.json](./0011-l2-infrastructure-bridge.rules.json).

---

## 2. Contexto
El sistema requiere una memoria funcional (RAG-DAG) para operar con coherencia ontológica. Implementar una solución temporal en L2 permite avanzar en la lógica de negocio sin bloquearse por la inmadurez de los adaptadores de bajo nivel (L4), siempre que se respete el aislamiento hexagonal.

---

## 3. Decisión: Puente de Infraestructura Temporal
Se autoriza a la Capa L2 (Brain) a instanciar y gestionar el archivo de base de datos `.aiwg/memory/loci.db` utilizando la librería nativa de Python (`kuzu`). 

---

## 4. Consecuencias
- **Disponibilidad Inmediata:** El Swarm puede usar memoria persistente desde ahora.
- **Acoplamiento Temporal:** Incurre en una deuda técnica controlada.
- **Protocolo de Mitigación:** La implementación en L2 debe seguir un patrón de Repositorio estricto en la carpeta `infrastructure` para facilitar el "swap" futuro por el adaptador de L4.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [0011-l2-infrastructure-bridge.feature](./0011-l2-infrastructure-bridge.feature)
- **Machine Rules:** [0011-l2-infrastructure-bridge.rules.json](./0011-l2-infrastructure-bridge.rules.json)

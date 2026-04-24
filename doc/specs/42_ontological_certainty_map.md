---
spec_id: "DE-V2-L2-42"
title: "Ontological Certainty Map"
status: "ACTIVE"
version: "2.2.0"
layer: "L2"
namespace: "io.dummie.v2.brain.ontology"
authority: "OVERSEER"
dependencies:
  - id: "DE-V2-L2-12"
    relationship: "EXTENDS"
tags: ["cognitive_core", "self_awareness", "epistemology"]
---

# 42. Ontological Certainty Map (El Sentido del "Yo" Técnico)

## Abstract
Este componente permite que el enjambre cuantifique matemáticamente lo que "sabe" y lo que "ignora" del repositorio. Utilizando el modelo de contexto 6D ([Spec 12](12_6d_context_model.md)), calcula un valor de certeza ontológica [0.0 - 1.0] para cada capa. Esto permite priorizar la investigación antes de intentar codificar arquitecturas inestables.

## 1. Cognitive Context Model (Ref)
Para los umbrales de certeza requeridos para codificar, los pesos heurísticos (Spec existence, TDD passing) y la ruta del mapa ontológico físico, consulte el archivo hermano [42_ontological_certainty_map.rules.json](./42_ontological_certainty_map.rules.json).

---

## 2. Alcance Operativo
El mapa se actualiza dinámicamente ante cada evento del sistema:
- **Incremento de Certeza:** Cuando una Spec pasa todos los validadores SDD.
- **Decremento de Certeza:** Ante fallos de tests TDD o detección de drift entre código y documentación.
- **Terra Incognita:** Módulos detectados físicamente pero sin representación en el modelo mental (Specs).

---

## 3. Derivada de Certeza (Mathematical Projection)
Dado que el 6D-Context ya no posee un Peso Semántico estático (`w`), la Certeza Ontológica se calcula como una proyección sobre el DAG 4D-TES en un punto $\{x, y, z\}$:

$$Certeza = \frac{\sum Tests \ en \ Verde}{\sum Nodos \ de \ Mutacion \ sin \ Auditar}$$

- **1.0 (Cristalino):** Todas las mutaciones en $\{x,y,z\}$ están auditadas y validadas.
- **$\ge$ 0.5 (Autorizado):** Nivel mínimo de certeza para que el Agente pueda emitir un nodo de Mutación en L1 (Código). Si es menor, el Sentinel bloquea la escritura.
- **0.0 (Terra Incognita):** Código existente pero sin historial causal de Specs o Tests. Se requiere una auditoría prioritaria.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [42_ontological_certainty_map.feature](./42_ontological_certainty_map.feature)
- **Machine Rules:** [42_ontological_certainty_map.rules.json](./42_ontological_certainty_map.rules.json)

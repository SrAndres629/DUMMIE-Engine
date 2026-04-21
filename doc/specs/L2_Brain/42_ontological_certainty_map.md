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

## 3. Escala de Certeza (Heurística)
- **1.0 (Cristalino):** Specs completas, ADRs alineados, Tests TDD en verde.
- **0.5 (Teórico):** Specs completas pero sin validación física en código.
- **0.0 (Ignorancia):** Código existente sin contrato ni documentación asociada.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [42_ontological_certainty_map.feature](./42_ontological_certainty_map.feature)
- **Machine Rules:** [42_ontological_certainty_map.rules.json](./42_ontological_certainty_map.rules.json)

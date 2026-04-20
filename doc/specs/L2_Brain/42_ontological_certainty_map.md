---
spec_id: "DE-V2-L2-42"
title: "Ontological Certainty Map"
status: "ACTIVE"
version: "1.0.0"
layer: "L2"
namespace: "io.dummie.v2.brain.ontology"
authority: "OVERSEER"
dependencies:
  - id: "DE-V2-L2-12"
    relationship: "EXTENDS"
tags: ["cognitive_core", "self_awareness", "epistemology"]
---

# Ontological Certainty Map (El Sentido del "Yo" Técnico)

## Abstract
Este componente permite que el enjambre cuantifique matemáticamente lo que "sabe" y lo que "ignora" del repositorio. Utilizando el modelo de contexto 6D (Spec 12), calcula un valor de certeza ontológica [0.0 - 1.0] para cada capa y Bounded Context. Esto permite priorizar los esfuerzos de investigación (`sw.strategy.discovery`) antes de intentar codificar arquitecturas inestables.

## 1. Alcance Operativo
El mapa se almacena físicamente en `.aiwg/ontological_map.json`. Se actualiza dinámicamente cuando:
- Una Spec pasa todos los SDD Validators (incremento de certeza).
- Un test TDD falla (decremento de certeza).
- Se introduce un nuevo Bounded Context sin Spec asociada (certeza inicial baja).

## 2. Escala de Certeza (Heurística)
- **1.0 (Cristalino):** Specs completas, ADRs alineados, Tests TDD 100% en verde.
- **0.5 (Teórico):** Specs completas, pero sin implementación de código.
- **0.0 (Terra Incognita):** Módulo detectado en código pero sin documentación ni specs.

---

## [MSA] Sibling Components
- **Executable Contract**: 42_ontological_certainty_map.feature
- **Machine Rules**: 42_ontological_certainty_map.rules.json

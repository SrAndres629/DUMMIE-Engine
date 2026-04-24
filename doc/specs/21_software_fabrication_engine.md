---
spec_id: "DE-V2-L2-21"
title: "Software Fabrication Engine (SFE)"
status: "ACTIVE"
version: "2.2.0"
layer: "L2"
namespace: "io.dummie.v2.brain"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L2-02"
    relationship: "REQUIRES"
tags: ["cognitive_core", "brain_logic", "industrial_sdd"]
---

# 21. Software Fabrication Engine (SFE)

## Abstract
La Software Fabrication Engine (SFE) es el orquestador cognitivo del sistema. Este componente rige la inteligencia agéntica, la gestión de la consistencia semántica y el aprendizaje continuo mediante ciclos Kaizen, asegurando que el proceso de fabricación de software sea determinista, auditable y soberano.

## 1. Cognitive Context Model (Ref)
Para los modos de fabricación (Greenfield, Refactor), los invariantes de Spec-First y los agentes requeridos para el consenso cognitivo, consulte el archivo hermano [21_software_fabrication_engine.rules.json](./21_software_fabrication_engine.rules.json).

---

## 2. Alcance Operativo
El componente opera dentro del Bounded Context del Cerebro (L2), interactuando con la Memoria 4D-TES y el Escudo L3. Su misión es garantizar que todo razonamiento agéntico sea coherente con la topología global y los invariantes de diseño del sistema.

---

## 3. Ciclo de Fabricación (Kaizen Loop)
La SFE implementa un bucle de refinamiento continuo:
1.  **Spec-Driven Analysis:** Validación de la intención contra los contratos existentes.
2.  **Sovereign Implementation:** Generación de código siguiendo la estratigrafía de 7 capas.
3.  **Metacognitive Audit:** Validación del resultado contra los Shields y el Ledger de Decisiones.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [21_software_fabrication_engine.feature](./21_software_fabrication_engine.feature)
- **Machine Rules:** [21_software_fabrication_engine.rules.json](./21_software_fabrication_engine.rules.json)

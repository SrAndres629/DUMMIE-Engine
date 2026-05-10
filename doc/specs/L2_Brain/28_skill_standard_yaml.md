---
spec_id: "DE-V2-L2-28"
title: "Estándar de Habilidades Agénticas (YAML)"
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

# 28. Estándar de Habilidades Agénticas (YAML)

## Abstract
Para que el Swarm de agentes pueda expandir sus capacidades de forma autónoma, el sistema formaliza el **Estándar de Habilidades (Skills)**. Este estándar define la estructura YAML de los manifiestos de habilidad, los protocolos de carga dinámica y el andamiaje recursivo necesario para que el sistema aprenda y ejecute nuevas funciones industriales.

## 1. Cognitive Context Model (Ref)
Para los invariantes de carga en caliente (Hotload), los archivos mandatarios de andamiaje y la política de versionado de habilidades, consulte el archivo hermano [28_skill_standard_yaml.rules.json](./28_skill_standard_yaml.rules.json).

---

## 2. Anatomía de una Skill
Toda habilidad debe residir en su propio directorio dentro de `skills/` y contener:
- **`SKILL.md`**: Narrativa y propósito de la habilidad.
- **`.feature`**: Escenarios de validación funcional.
- **`.rules.json`**: Invariantes técnicos y restricciones de ejecución.

---

## 3. Evolución de Habilidades (Kaizen)
Tras un ciclo de mejora **Kaizen ([Spec 27](27_kaizen_loop_refinement.md))**, el sistema puede emitir una nueva versión de la habilidad. El despliegue es atómico y cuenta con mecanismos de **Rollback de Habilidad** si se detectan regresiones en el Bucle Ralph.

---

## 4. Andamiaje Recursivo (Recursive Skill Scaffolding)
Inspirado por la capacidad de auto-crecimiento, el sistema permite generar nuevas capacidades ante gaps operacionales:
1.  **Gap Discovery:** Identificación de una tarea sin skill activa.
2.  **Contract Scaffolding:** Generación de directorio con archivos MSA válidos.
3.  **Bootstrap Audit:** Auditoría de integridad por el Sentinel (L3).
4.  **Hot-Registration:** Indexación dinámica en el registro de habilidades.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [28_skill_standard_yaml.feature](./28_skill_standard_yaml.feature)
- **Machine Rules:** [28_skill_standard_yaml.rules.json](./28_skill_standard_yaml.rules.json)

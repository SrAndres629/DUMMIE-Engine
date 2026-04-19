---
spec_id: "DE-V2-L2-28"
title: "Estándar de Habilidades Agénticas (YAML)"
status: "ACTIVE"
version: "1.0.0"
layer: "L2"
namespace: "io.dummie.v2.brain"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L2-02"
    relationship: "REQUIRES"
tags: ["cognitive_core", "brain_logic", "industrial_sdd"]
---

# Estándar de Habilidades Agénticas (YAML)

## Abstract
Esta especificación define un componente crítico del plano cognitivo (Brain L2). Se centra en la orquestación de la inteligencia agéntica, la gestión de la consistencia semántica y el aprendizaje continuo mediante ciclos Kaizen.

## 1. Alcance Operativo
El componente opera dentro del Bounded Context del Cerebro, interactuando con la Memoria 4D-TES y el Escudo L3 para garantizar que todo razonamiento sea coherente con la topología global del sistema.

## 5. Evolución de Habilidades (Kaizen)
Tras un ciclo de mejora **Kaizen ([Spec 27](27_kaizen_loop_refinement.md))**, el sistema puede emitir una nueva versión de la habilidad. El despliegue de habilidades es atómico:
- Si la nueva versión falla en el **Bucle Ralph**, el sistema realiza un **Rollback de Habilidad** a la versión anterior estable.

## 6. Andamiaje Recursivo (Recursive Skill Scaffolding)
Inspirado por la capacidad de **Auto-Crecimiento de OpenClaw**, el sistema permite que un agente genere físicamente nuevas capacidades si detecta un gap operacional:

1.  **Gap Discovery:** El Cerebro L2 identifica una tarea para la cual no existe una Skill activa en el registro.
2.  **Contract Scaffolding:** El agente genera un nuevo directorio en `skills/` con un `SKILL.md` y archivos MSA (.feature / .rules.json) válidos.
3.  **Bootstrap Audit:** El Sentinel (L3) audita el nuevo andamiaje contra los invariantes de seguridad.
4.  **Hot-Registration:** La nueva habilidad se indexa dinámicamente sin necesidad de reiniciar el Overseer.

---

## [MSA] Sibling Components
- **Executable Contract**: 28_skill_standard_yaml.feature
- **Machine Rules**: 28_skill_standard_yaml.rules.json

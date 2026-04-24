---
spec_id: "DE-V2-L0-33"
title: "Perfil de Personalidad y Mood Estratégico"
status: "ACTIVE"
version: "2.2.0"
layer: "L0"
namespace: "io.dummie.v2.governance.personality"
authority: "PAH"
dependencies:
  - id: "DE-V2-[ADR-004](../../01_architecture/adr/0004-project-personality.md)"
    relationship: "REFINES"
tags: ["personality", "mood_engineering", "industrial_sdd"]
---

# 33. Perfil de Personalidad y Mood Estratégico

## Abstract
La personalidad de un proyecto no es un rasgo emocional, sino el conjunto de restricciones técnicas y el estilo histórico que define su identidad. Esta especificación formaliza el **Chip de Personalidad** del DUMMIE Engine, permitiendo que los agentes "cambien de chip" instantáneamente basándose en hiperparámetros de gobernanza.

## 1. Cognitive Context Model (Ref)
Para los ejes vectoriales de gobernanza (agresividad, rigor, deuda, seguridad), los invariantes de identidad y las reglas de inyección de Mood, consulte el archivo hermano [33_persistent_personality_mood.rules.json](./33_persistent_personality_mood.rules.json).

---

## 2. El Ancla de Identidad (SOUL.md)
La identidad del proyecto se divide en dos anclas:
- **`.aiwg/identity.json`**: Restricciones técnicas inamovibles definidas por el PAH.
- **`SOUL.md`**: El anclaje narrativo y evolutivo del sistema. Es un archivo mutable donde el agente registra su autopercepción y su "Mood" actual.

---

## 3. Desplazamiento de Alma (Dynamic Soul Shifting)
Inspirado por la capacidad de intercambiar perfiles de identidad dinámicamente, el sistema permite asunciones de "máscaras" cognitivas:
1.  **Shift Intent:** Detección de sub-optimalidad de personalidad para la tarea.
2.  **Template Loading:** Carga de un `soul_template.md` desde el registro de Blueprints ([Spec 25](../L4_Edge/25_blueprint_registry.md)).
3.  **Context Re-Mapping:** Actualización del modelo 6D con los nuevos sesgos.

---

## 4. Inyección de "Mood" en el Swarm
Cuando un agente se activa, el **Overseer (L0)** realiza una inyección de contexto:
1.  **Lectura:** El sistema lee el `.aiwg/identity.json`.
2.  **Adaptación de Prompt:** Traducción de hiperparámetros en restricciones de sistema.
3.  **Veto de Diseño:** El `S-Shield` ([Spec 04](../L3_Shield/04_anti_ignorance_shields.md)) califica las propuestas según estos parámetros.

---

## 5. Gobernanza del Cambio de Perfil
- Solo el **PAH (Usuario)** puede modificar el `identity.json` directamente.
- Al detectarse un cambio, el sistema lanza una **Alerta de Re-Alineación Global**.
- **Isomorfismo:** El sistema garantiza que el código producido "hable" con el mismo tono técnico.

---

## 6. Protocolo de Graph-Hydration (L0 -> L4)
Para evitar que la personalidad sea solo "texto estático":
1.  **Monitorización:** El Librarian vigila cambios en `.aiwg/identity.json`.
2.  **Mapping:** Traducción de rasgos a nodos `PersonalityTrait` en KùzuDB.
3.  **Relinking:** Arcos de influencia hacia los directorios de código afectados.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [33_persistent_personality_mood.feature](./33_persistent_personality_mood.feature)
- **Machine Rules:** [33_persistent_personality_mood.rules.json](./33_persistent_personality_mood.rules.json)

---
spec_id: "DE-V2-L0-33"
title: "Perfil de Personalidad y Mood Estratégico"
status: "ACTIVE"
version: "1.0.0"
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
La personalidad de un proyecto no es un rasgo emocional, sino el conjunto de restricciones técnicas y el estilo histórico que define su identidad. Esta especificación formaliza el **Chip de Personalidad** del DUMMIE Engine, permitiendo que los agentes "cambien de chip" instantáneamente al cambiar de contexto, basándose en hiperparámetros de gobernanza.

## 1. Axiomas de Personalidad (Design Intent)
La personalidad del sistema no se define por prosa, sino por la interacción de cuatro ejes vectoriales de gobernanza. La configuración binaria de estos ejes reside en el archivo de reglas MSA hermano.

- **Agresividad de Refactorización:** Define el umbral de ROI necesario para proponer cambios estructurales.
- **Rigor de Abstracción:** Obligatoriedad de patrones DDD, Hexagonal y tipado estricto.
- **Tolerancia a Deuda:** Prioridad de la velocidad de entrega (MVP) frente a la pureza técnica.
- **Sesgo de Seguridad:** Nivel de paranoia y aislamiento de procesos (Zero-Trust).

---

## 2. El Ancla de Identidad (SOUL.md)
La identidad del proyecto se divide en dos anclas:
- **`profile.json`**: Restricciones técnicas inamovibles definidas por el PAH.
- **`SOUL.md`**: El anclaje narrativo y evolutivo del sistema. Es un archivo mutable donde el agente registra su autopercepción, sus hitos de aprendizaje (Necro-Learning) y su "Mood" actual.

## 3. Desplazamiento de Alma (Dynamic Soul Shifting)
Inspirado por la capacidad de **OpenClaw** de intercambiar perfiles de identidad dinámicamente, el sistema permite que el agente asuma diferentes "máscaras" cognitivas según el contexto:

1.  **Shift Intent:** El agente detecta que su personalidad actual no es la óptima para la tarea (p. ej. un "Escritor Creativo" realizando una "Auditoría de Seguridad").
2.  **Template Loading:** El sistema carga un `soul_template.md` desde el registro de Blueprints ([Spec 25](../L4_Edge/25_blueprint_registry.md)).
3.  **Context Re-Mapping:** El modelo de contexto 6D se actualiza con los nuevos sesgos, valores y restricciones de la nueva identidad.
4.  **Ephemeral Memory:** Los recuerdos de la "Vida Anterior" (persona anterior) se conservan como contexto histórico, pero la prioridad operacional se transfiere al alma activa.

---

## [MSA] Sibling Components
- **Executable Contract**: [33_persistent_personality_mood.feature](33_persistent_personality_mood.feature)
- **Machine Rules**: [33_persistent_personality_mood.rules.json](33_persistent_personality_mood.rules.json)
- **Aggressiveness (0.3):** Prioriza la estabilidad sobre la refactorización innecesaria. El agente solo propone cambios si el ROI es claro.
- **Abstraction Rigor (1.0):** No se permiten atajos. Toda lógica debe seguir la estratigrafía de 7 capas y los contratos Protobuf.
- **Security Bias (1.0):** El aislamiento de procesos (Bubblewrap) y la validación del Escudo son innegociables.

---

### 3. Inyección de "Mood" en el Swarm
Cuando un agente (Coder, Sentinel, Investigator) se activa, el **Overseer (L0)** realiza una inyección de contexto:
1.  **Lectura:** El sistema lee el `profile.json`.
2.  **Adaptación de Prompt:** Los hiperparámetros se traducen en restricciones de sistema (*System Instructions*).
3.  **Veto de Diseño:** El `S-Shield` ([Spec 04](../L3_Shield/04_anti_ignorance_shields.md)) utiliza estos parámetros para calificar las propuestas del Coder. Un `abstraction_rigor: 1.0` vetará automáticamente cualquier código spaghetti o fuera de capas.

---

## 4. Gobernanza del Cambio de Perfil
- Solo el **PAH (Usuario)** puede modificar el `profile.json` directamente.
- Al detectarse un cambio en el perfil, el sistema lanza una **Alerta de Re-Alineación Global** en el Command Canvas, forzando a los agentes a re-evaluar sus tareas en curso bajo el nuevo "Mood".
- **Isomorfismo:** El sistema garantiza que el código producido "hable" con el mismo tono técnico, independientemente de qué modelo de IA (GPT-4, Claude, Gemini) lo haya fabricado.

---

## 5. Protocolo de Graph-Hydration (L0 -> L4)
Para evitar que la personalidad sea solo "texto estático", el sistema implementa una **Cámara Espejo** en el Palacio de Loci:
1.  **Monitorización:** El Librarian (L2) vigila cambios en `.aiwg/personality/`.
2.  **Mapping:** Cada rasgo (`trait`) y restricción (`forbidden_pattern`) se traduce a un nodo `PersonalityTrait` en KùzuDB.
3.  **Relinking:** Se establecen arcos de influencia hacia los directorios de código afectados (ej: `security_bias` influye en `layers/l3_shield`).
4.  **Pulse Update:** La actualización del grafo ocurre tras cada commit del PAH, asegurando que el GraphRAG de los agentes siempre opere sobre el "Mood" vigente.

---

## 5. Vinculación Global
El perfil de personalidad influye en todas las capas del sistema, desde la selección de herramientas en L1 hasta la generación de trazas en L6. Para más detalles sobre los invariantes técnicos y la estructura del motor de Shield, consulte el archivo de reglas [33_persistent_personality_mood.rules.json](33_persistent_personality_mood.rules.json).

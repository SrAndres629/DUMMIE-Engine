---
spec_id: "DE-V2-L2-36"
title: "Memoria Cognitiva y Ledger de Sesión"
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

# 36. Memoria Cognitiva y Ledger de Sesión

## Abstract
El Ledger de Sesión gestiona la **Memoria de Trabajo Efímera** del sistema. A diferencia del Ledger de Decisiones (L2-34) que es de larga duración, este componente captura el "Stream of Consciousness" de los agentes durante una sesión activa, indexando vectores de pensamiento, acciones e intenciones para permitir el razonamiento contextual y la recuperación ante fallos locales.

## 1. Cognitive Context Model (Ref)
Para la ruta del ledger de sesión, los metadatos obligatorios (Thought Vector, Action) y los disparadores de compresión de memoria, consulte el archivo hermano [36_cognitive_memory_session_ledger.rules.json](./36_cognitive_memory_session_ledger.rules.json).

---

## 2. Captura del Estado del Ego
Cada paso de razonamiento del agente se registra como un `EgoState`:
- **Thought Vector:** Representación latente del razonamiento actual.
- **Action:** Intención física o llamada a herramienta emitida.
- **Tick:** Timestamp lógico para sincronización con el 4D-TES.

---

## 3. Persistencia y Apoptosis
El Ledger de Sesión es de naturaleza transitoria:
- **Append-Only:** Escritura continua durante la sesión.
- **Crystallization:** Al finalizar la sesión ([Spec 49](../L0_Overseer/49_sovereign_cognitive_closure_protocol.md)), los hitos relevantes se destilan hacia la memoria semántica y el ledger de sesión se archiva o se somete a apoptosis controlada.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [36_cognitive_memory_session_ledger.feature](./36_cognitive_memory_session_ledger.feature)
- **Machine Rules:** [36_cognitive_memory_session_ledger.rules.json](./36_cognitive_memory_session_ledger.rules.json)

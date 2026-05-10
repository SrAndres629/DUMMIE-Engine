---
spec_id: "DE-V2-L2-36"
title: "Memoria Cognitiva y Ledger de Sesión"
status: "ACTIVE"
version: "2.3.0"
layer: "L2"
namespace: "io.dummie.v2.brain"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L2-02"
    relationship: "REQUIRES"
  - id: "DE-ADR-0016"
    relationship: "IMPLEMENTS"
tags: ["cognitive_core", "brain_logic", "industrial_sdd", "mem0"]
---

# 36. Memoria Cognitiva y Ledger de Sesión

## Abstract
El Ledger de Sesión gestiona la **Memoria de Trabajo Efímera** del sistema. A diferencia del Ledger de Decisiones (L2-34) que es de larga duración, este componente captura el "Stream of Consciousness" de los agentes durante una sesión activa, indexando vectores de pensamiento, acciones e intenciones para permitir el razonamiento contextual y la recuperación ante fallos locales. Se apoya en el engranaje **Mem0** para la persistencia semántica de largo plazo.

## 1. Cognitive Context Model (Ref)
Para la ruta del ledger de sesión, los metadatos obligatorios (Thought Vector, Action) y los disparadores de compresión de memoria, consulte el archivo hermano [36_cognitive_memory_session_ledger.rules.json](./36_cognitive_memory_session_ledger.rules.json).

---

## 2. Captura del Estado del Ego
Cada paso de razonamiento del agente se registra como un `EgoState`:
- **Thought Vector:** Representación latente del razonamiento actual.
- **Action:** Intención física o llamada a herramienta emitida.
- **Tick:** Timestamp lógico para sincronización con el 4D-TES.

---

## 3. Persistencia y Apoptosis (Mem0 Integration)
El Ledger de Sesión es de naturaleza transitoria:
- **Append-Only:** Escritura continua durante la sesión.
- **Crystallization:** Al finalizar la sesión ([Spec 49](../L0_Overseer/49_sovereign_cognitive_closure_protocol.md)), los hitos relevantes se destilan hacia el engranaje **Mem0** ([Gear Registry](../../shared/gear_registry.json)).
- **Apoptosis:** Una vez cristalizada la información útil, el ledger de sesión se archiva o se elimina para liberar recursos de hardware.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [36_cognitive_memory_session_ledger.feature](./36_cognitive_memory_session_ledger.feature)
- **Machine Rules:** [36_cognitive_memory_session_ledger.rules.json](./36_cognitive_memory_session_ledger.rules.json)

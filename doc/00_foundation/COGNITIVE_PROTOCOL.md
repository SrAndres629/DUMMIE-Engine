---
spec_id: "DE-V2-L0-PROTOCOL"
title: "Protocolo de Ingesta y Cristalización Cognitiva"
status: "ACTIVE"
version: "1.2.0"
layer: "L0"
namespace: "io.dummie.v2.foundation"
authority: "ARCHITECT"
tags: ["foundation", "cognitive_protocol", "memory_management"]
---

# Protocolo de Ingesta y Cristalización Cognitiva

## Abstract
Este protocolo rige cómo los agentes (L2 Brain) deben consumir y generar conocimiento dentro del DUMMIE Engine. Su misión es garantizar la soberanía de la información, evitar la duplicidad de errores y asegurar que todo aprendizaje sea cristalizado de forma determinista en el Ledger del sistema.

## 1. Cognitive Context Model (Ref)
Para los invariantes técnicos del flujo de memoria, consulte el archivo hermano [COGNITIVE_PROTOCOL.rules.json](./COGNITIVE_PROTOCOL.rules.json).

---

## 2. Procedimiento de Onboarding (Lectura Obligatoria)
Antes de realizar cualquier cambio físico en el monorepo, todo agente DEBE realizar este escaneo secuencial:
1.  **Indexar [ATLAS.md](../ATLAS.md):** Para entender la topología actual del monorepo.
2.  **Escanear [.aiwg/memory/](../../.aiwg/memory/):** 
    -   `decisions.jsonl`: ¿Se ha decidido algo antes sobre este componente?
    -   `lessons.jsonl`: ¿Qué falló la última vez que alguien tocó esto?
    -   `ambiguities.jsonl`: ¿Qué dudas resolvió el PAH recientemente?
3.  **Auditar Restricciones Arquitectónicas Activas (ADRs):** El agente Tech Lead (Nodo 3) **DEBE** procesar todos los archivos `.rules.json` en `doc/01_architecture/adr/`. Las reglas de los ADRs con estado `ACCEPTED` son vinculantes.

---

## 3. Protocolo de Escritura (Crystallization)
El agente no espera al final de la sesión; cristaliza la memoria en tiempo real tras hitos críticos:

### A. Registro de Decisiones
Si el usuario aprueba un cambio arquitectónico o una implementación Greenfield.
- **Formato:** JSONL alineado con `memory.proto`.
- **Destino:** `.aiwg/memory/decisions.jsonl`.

### B. Registro de Lecciones (Post-Mortem)
Si el agente cometió un error de sintaxis, rompió un test o recibió una corrección del PAH.
- **Formato:** JSONL alineado con `memory.proto`.
- **Destino:** `.aiwg/memory/lessons.jsonl`.

### C. Registro de Ambigüedades
Si el agente tuvo que usar el protocolo `Ask-User-First` para eliminar una indeterminación.
- **Formato:** JSONL alineado con `memory.proto`.
- **Destino:** `.aiwg/memory/ambiguities.jsonl`.

---

## 4. Invariante de Validación
Cualquier entrada de memoria será validada por el **SDD Auditor (doc/04_forge/sdd_validator.py)**. Las entradas que violen el esquema Protobuf de Layer 1 serán marcadas como `CORRUPTED`.

---

## 5. Protocolo de Cierre Soberano (SCCP)
Al final de cada sesión, es MANDATORIO ejecutar el ritual de cierre definido en la **[Spec 49](../specs/L0_Overseer/49_sovereign_cognitive_closure_protocol.md)**.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [COGNITIVE_PROTOCOL.feature](./COGNITIVE_PROTOCOL.feature)
- **Machine Rules:** [COGNITIVE_PROTOCOL.rules.json](./COGNITIVE_PROTOCOL.rules.json)

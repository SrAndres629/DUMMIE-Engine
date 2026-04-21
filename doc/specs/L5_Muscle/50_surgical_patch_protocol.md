---
spec_id: "DE-V2-L5-50"
title: "Protocolo de Parche Quirúrgico (Surgical Patching)"
status: "ACTIVE"
version: "2.2.0"
layer: "L5"
namespace: "io.dummie.v2.muscle.patching"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L5-16"
    relationship: "REFINES_IO"
  - id: "DE-V2-L3-04"
    relationship: "AUDITED_BY"
tags: ["muscle_layer", "patching", "atomic_diff", "integrity_check"]
---

# 50. Protocolo de Parche Quirúrgico (Surgical Patching)

## Abstract
Para evitar la corrupción de archivos y garantizar el determinismo en la fabricación de software, el sistema implementa el **Protocolo de Parche Quirúrgico**. En lugar de sobrescribir archivos, el Músculo L5 aplica parches atómicos basados en Diffs Soberanos. Cada modificación requiere una validación previa del hash de integridad, asegurando que el agente solo modifique el código si el estado físico en disco coincide exactamente con su modelo mental.

## 1. Cognitive Context Model (Ref)
Para el tamaño máximo del parche, la política de no-fuzzy-matching y los requisitos de cabeceras de integridad (Target Hash, Patch Type), consulte el archivo hermano [50_surgical_patch_protocol.rules.json](./50_surgical_patch_protocol.rules.json).

---

## 2. El Diff Soberano (Mojo Protocol)
Un Parche Quirúrgico es una operación atómica que contiene:
- **Target Hash:** SHA-256 del contenido actual del archivo en disco.
- **Replacement Chunk:** Fragmento exacto de código con coordenadas de líneas (Inicio/Fin).
- **Integrity Validation:** Verificación obligatoria en Layer 5 antes de la escritura física.
- **Detach Exception:** Si el hash en disco no coincide, el sistema lanza una excepción que obliga al agente a re-hidratar su contexto LSP ([Spec 49](../L4_Edge/49_lsp_context_hydration_protocol.md)) antes de reintentar.

---

## 3. Resolución de Conflictos y Transaccionalidad
- **Read-Check-Write:** Ciclo de vida atómico para prevenir condiciones de carrera (Race Conditions).
- **Atomic Multi-file Edit:** Si una tarea afecta a múltiples archivos, todos los parches deben aplicarse con éxito o el sistema revierte la transacción completa.
- **Undo Snapshots:** Cada parche exitoso genera un snapshot efímero en la Necro-Learning Pipeline para permitir rollbacks instantáneos ante errores de lógica detectados por el Auditor.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [50_surgical_patch_protocol.feature](./50_surgical_patch_protocol.feature)
- **Machine Rules:** [50_surgical_patch_protocol.rules.json](./50_surgical_patch_protocol.rules.json)

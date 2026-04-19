---
spec_id: "DE-V2-L5-50"
title: "Protocolo de Parche Quirúrgico (Surgical Patching)"
status: "ACTIVE"
version: "1.0.0"
layer: "L5"
namespace: "io.dummie.v2.muscle.patching"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L5-16"
    relationship: "REFINES_IO"
  - id: "DE-V2-L3-04"
    relationship: "AUDITED_BY"
tags: ["muscle_layer", "patching", "atomic_diff", "integrity_check", "claw_ism"]
---

# 50. Protocolo de Parche Quirúrgico (Surgical Patching)

## Abstract
Para escalar la Software Fabrication Engine (SFE) a proyectos de gran escala y evitar la corrupción de archivos por cambios asíncronos, esta especificación introduce el **Protocolo de Parche Quirúrgico**. El sistema evoluciona de "sobrescribir archivos" a "aplicar parches atómicos". Cada modificación se transmite como un Diff Soberano con sumas de comprobación (hashes) de integridad, garantizando que el agente solo modifique el código si el estado del archivo físico coincide exactamente con su modelo mental.

## 1. El Diff Soberano (L5 Muscle Protocol)
Un Parche Quirúrgico se compone de:

- **Target Hash**: El SHA-256 del contenido actual del archivo.
- **Replacement Chunk**: El fragmento exacto de código (líneas de inicio/fin) a ser modificado.
- **Integrity Validation**: Un paso previo obligatorio en Layer 5 que compara el hash en disco con el `Target Hash`.

Si los hashes no coinciden (ej. el usuario editó el archivo mientras el agente pensaba), el Muscle L5 lanza una **Excepción de Desacople (Detach Exception)** y el agente debe re-hidratar el contexto semántico antes de reintentar.

---

## 2. Resolución de Conflictos y Optimismo
El protocolo prioriza el **Optimismo Cauteloso**:
1.  **Read-Check-Write**: Ciclo atómico para evitar race conditions.
2.  **Visual Feedback**: El Canvas L6 muestra el diff propuesto antes de la aplicación física si el `mood_aggressiveness` es bajo.
3.  **Undo Buffering**: Cada parche exitoso genera un snapshot temporal en la **Necro-Learning Pipeline ([Spec 35](35_necro_learning_pipeline.md))** para permitir rollbacks instantáneos.

---

## 3. Invariantes de Aplicación
- **No-Fuzzy-Matching**: El sistema rechaza parches que no coincidan exactamente con el `TargetContent`. No se permite el matching difuso para evitar errores lógicos.
- **Atomicidad Transaccional**: Si una tarea requiere parchear 3 archivos, la operación debe ser atómica o revertirse por completo.

---

## [MSA] Sibling Components
- **Executable Contract**: [50_surgical_patch_protocol.feature](50_surgical_patch_protocol.feature)
- **Machine Rules**: [50_surgical_patch_protocol.rules.json](50_surgical_patch_protocol.rules.json)

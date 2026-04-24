---
spec_id: "DE-V2-L0-48"
title: "Protocolo de Cristalización de Integridad Arquitectónica (ACIP)"
status: "ACTIVE"
version: "2.2.0"
layer: "L0"
namespace: "io.dummie.v2.overseer.integrity"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-06"
    relationship: "REFINES"
tags: ["governance", "integrity", "acip", "industrial_sdd"]
---

# 48. Protocolo de Cristalización de Integridad Arquitectónica (ACIP)

## Abstract
DUMMIE Engine es un sistema de auto-documentación perpetua gobernado por el **Protocolo ACIP**. Ninguna decisión física (código o infraestructura) queda huérfana de su justificación teórica, eliminando la acumulación de deuda de conocimiento y garantizando la soberanía de los activos en el monorepo.

## 1. Cognitive Context Model (Ref)
Para los invariantes de integridad de directorios, las reglas de cristalización mandataria en el Ledger y las políticas de exclusión de bloatware en la unidad principal, consulte el archivo hermano [48_architectural_integrity_and_knowledge_crystallization.rules.json](./48_architectural_integrity_and_knowledge_crystallization.rules.json).

---

## 2. Los Tres Pilares de la Integridad

### 2.1. Cristalización Mandataria (Causal Crystallization)
Tras cada hito de implementación exitosa, el agente ejecutor DEBE cristalizar el conocimiento en la memoria agéntica (`.aiwg/memory/`):
1.  **Decisión**: Por qué se implementó de esta forma.
2.  **Lección**: Qué fallos ocurrieron y cómo se evitaron.
3.  **Ambigüedad**: Compromisos pragmáticos tomados durante la fabricación.

### 2.2. Política de Soberanía de Disco (Anti-Bloatware)
La unidad de sistema operativo es sagrada y solo debe contener **CÓDIGO FUENTE E INTENCIÓN**.
- **Regla**: Todo artefacto derivado (> 50MB) DEBE residir en la **Unidad D (/media/datasets)**.
- **Mecanismo**: Uso obligatorio de enlaces simbólicos (symlinks).

### 2.3. Control de Drift (Sincronización SDD)
Cualquier divergencia física respecto a la Spec original DEBE ser documentada como un "Compromiso de Runtime" antes del cierre de la sesión para evitar la entropía arquitectónica.

---

## 3. Criterios de Aceptación (AC)
- **AC-48.1**: Reproducibilidad total del entorno mediante Specs y Memory Ledger.
- **AC-48.2**: El monorepo no debe exceder los 500MB de peso físico.
- **AC-48.3**: Trazabilidad total: No existe código sin contrato ni contrato sin registro de decisión.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [48_architectural_integrity_and_knowledge_crystallization.feature](./48_architectural_integrity_and_knowledge_crystallization.feature)
- **Machine Rules:** [48_architectural_integrity_and_knowledge_crystallization.rules.json](./48_architectural_integrity_and_knowledge_crystallization.rules.json)

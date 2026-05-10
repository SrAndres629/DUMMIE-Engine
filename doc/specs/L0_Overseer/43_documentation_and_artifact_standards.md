---
spec_id: "DE-V2-L0-43"
title: "Estándares de Documentación y Artefactos"
status: "ACTIVE"
version: "2.2.0"
layer: "L0"
namespace: "io.dummie.v2.governance.docs"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-[ADR-008](../../01_architecture/adr/0008-hierarchical-domain-specific-documentation.md)"
    relationship: "IMPLEMENTS"
tags: ["documentation_standards", "normative", "modular_spec"]
---

# 43. Estándares de Documentación y Artefactos

## Abstract
Para que una **Software Fabrication Engine (SFE)** sea escalable y autónoma, sus planos (Specs) deben seguir un orden industrial riguroso. Esta especificación define los estándares obligatorios de nomenclatura, estructura y jerarquía para toda la documentación del ecosistema DUMMIE Engine.

## 1. Cognitive Context Model (Ref)
Para los patrones de nombrado de carpetas, los hermanos MSA requeridos y las reglas de coincidencia de capas entre frontmatter y ruta física, consulte el archivo hermano [43_documentation_and_artifact_standards.rules.json](./43_documentation_and_artifact_standards.rules.json).

---

## 2. Topología del Directorio de Specs
Toda especificación debe residir en una carpeta que corresponda a su capa de soberanía (L0-L6):
- **L0_Overseer:** Gobernanza y Estado Global.
- **L1_Nervous:** Conectividad y Contratos.
- **L2_Brain:** Cognición y Razonamiento.
- **L3_Shield:** Seguridad e Invariantes.
- **L4_Edge:** LST y Ontologías.
- **L5_Muscle:** Hardware y SIMD.
- **L6_Skin:** Interfaces y Telemetría.

---

## 3. Nomenclatura de Archivos (Hermanos MSA)
Cada especificación se compone de una tríada indivisible:
1.  **NN_name.md (Narrativa)**: Fuente Semántica para Humanos.
2.  **NN_name.feature (Ejecutable)**: Escenarios Gherkin con métricas.
3.  **NN_name.rules.json (Determinismo)**: Fuente de Verdad para Máquinas.

---

## 4. Requisitos de Frontmatter
Todo archivo `.md` y `.feature` basado en SDD V3 debe incluir un header YAML con `spec_id`, `layer`, `authority` y `namespace`.

---

## 5. Soberanía Estructural y No-Redundancia (Axioma de SSOT)
Para evitar la entropía técnica, se establece el **Axioma de No-Redundancia**:
- **Prohibido** incluir bloques de código JSON extensos dentro del Markdown si estos ya residen en el archivo `.rules.json`.
- El Markdown debe proporcionar una **Descripción Funcional** y apuntar al archivo hermano para la especificación binaria.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [43_documentation_and_artifact_standards.feature](./43_documentation_and_artifact_standards.feature)
- **Machine Rules:** [43_documentation_and_artifact_standards.rules.json](./43_documentation_and_artifact_standards.rules.json)

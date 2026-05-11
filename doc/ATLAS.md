---
spec_id: "DE-V2-ATLAS"
title: "DUMMIE Engine: Sovereign Documentation Atlas (HSD)"
status: "ACTIVE"
version: "2.0.0"
layer: "L0"
namespace: "io.dummie.v2.atlas"
authority: "ARCHITECT"
tags: ["atlas", "navigation", "hierarchical_documentation"]
---

# DUMMIE Engine: Sovereign Documentation Atlas (HSD)

## Abstract
Este es el punto de entrada de **Grado Cero** para la navegación cognitiva y operativa del monorepo. Sigue una arquitectura **Hierarchical Sovereign Documentation (HSD)** diseñada para la eficiencia de agentes de IA, garantizando que el Swarm tenga un mapa topológico claro del conocimiento del sistema.

## 1. Cognitive Context Model (Ref)
Para la estructura técnica de la jerarquía documental, consulte el archivo hermano [ATLAS.rules.json](./ATLAS.rules.json).

---

## 2. 🗺️ Mapa de Loci Documental

### [00_Foundation](./00_foundation/) - DEPT. DE ESTRATEGIA (LA INTENCIÓN)
*   **[Vision Manifesto](./00_foundation/vision_manifesto.md):** El "Por qué" inmutable y los axiomas del sistema.
*   **[Cognitive Protocol](./00_foundation/COGNITIVE_PROTOCOL.md):** El manual de operaciones para el uso y generación de memoria agéntica.
*   **[Philosophy](./00_foundation/philosophy/):** Ensayos y bases teóricas del DUMMIE OS.

### [01_Architecture](./01_architecture/) - DEPT. DE ARQUITECTURA (EL BLUEPRINT)
*   **[ADR](./01_architecture/adr/):** Historial de Decisiones de Arquitectura (Commitment Log).
*   **[Diagrams](./01_architecture/diagrams/):** Modelos C4 y flujos Mermaid de la estructura 7-capas.

### [02_Atlas](./02_atlas/) - DEPT. DE ARQUITECTURA (LA REALIDAD)
*   **[Physical Map](./02_atlas/PHYSICAL_MAP.md):** Mapa de sincronización de archivos y topología del disco.
*   **[Headers Index](./02_atlas/headers.md):** Índice maestro de stubs y contratos de la interfaz.

### [03_Pulse](./03_pulse/) - DEPT. DE QA Y AUDITORÍA (EL RITMO)
*   **[Heartbeat](./03_pulse/HEARTBEAT.md):** Tareas activas, monitores de vuelo y gobernanza operativa.

### [04_Forge](./04_forge/) - DEPT. DE INGENIERÍA DE PLANTA (LAS HERRAMIENTAS)
*   **[SDD Validator](./04_forge/sdd_validator.py):** Herramienta de auditoría semántica para el cumplimiento de Specs.

### [05_Archive](./05_archive/) - HISTORIAL
*   **[Inventory V1](./05_archive/inventory_v1.md):** Registro histórico de la migración inicial.
*   **[Legacy Extracts](./05_archive/legacy_extracts/):** PDF y textos de referencia técnica externa.

### [Specs](./specs/) - LA EJECUCIÓN (Source of Truth)
Organizado por capas soberanas L0 (Elixir) a L6 (User Interface).

---

## 3. Protocolo de Uso
Todo agente nuevo debe indexar este archivo antes de realizar cambios estructurales. La verdad reside en las `/specs/`, pero el contexto reside en el `/doc/Atlas`.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [ATLAS.feature](./ATLAS.feature)
- **Machine Rules:** [ATLAS.rules.json](./ATLAS.rules.json)

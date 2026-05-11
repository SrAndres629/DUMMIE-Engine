---
spec_id: "DE-V2-L2-29"
title: "Arquitectura de la Estación de Diseño (Workflow)"
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

# 29. Arquitectura de la Estación de Diseño (Workflow)

## Abstract
La Estación de Diseño define el **Entorno de Trabajo Cognitivo** donde los agentes colaboran para la creación de nuevos componentes. Este workflow garantiza que toda propuesta de diseño pase por una serie de estados deterministas (Draft, Audit, Active) y sea validada recursivamente contra el Palacio de Loci y las reglas de colisión arquitectónica.

## 1. Cognitive Context Model (Ref)
Para los estados del workflow, los requisitos de autoridad (Architect L0) y los invariantes de detección de colisiones en el grafo de dependencias, consulte el archivo hermano [29_design_station_workflow.rules.json](./29_design_station_workflow.rules.json).

---

## 2. El Ciclo de Vida del Diseño (Causal Projection)
En un sistema 4D-TES puro, **no existen los estados mutables**. Un componente no "cambia" de DRAFT a ACTIVE. El estado es una **Proyección Matemática (View)** calculada leyendo la cadena de eventos:

1.  **DRAFT:** Estado por defecto cuando un nodo es creado (`IntentType = MUTATION`).
2.  **AUDIT:** Estado derivado cuando un Auditor o el Sentinel L3 anexa un nodo de revisión al DAG apuntando al `causal_hash` del DRAFT.
3.  **ACTIVE:** Estado derivado exclusivamente cuando un `DecisionRecord` (emitido por `ARCHITECT_L0` o superior) apunta al `causal_hash` del nodo con una resolución de aprobación.
4.  **DEPRECATED:** Proyección cuando un nuevo `DecisionRecord` revoca el estado anterior.

---

## 3. Detección de Colisiones
Antes de transicionar a `ACTIVE`, la Estación de Diseño realiza un escaneo de **Blast Radius**:
- Identificación de componentes afectados por el cambio.
- Validación de que ningún contrato (`.feature`) sea violado por la nueva implementación.
- Aseguramiento de que no se introducen dependencias circulares prohibidas por la estratigrafía.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [29_design_station_workflow.feature](./29_design_station_workflow.feature)
- **Machine Rules:** [29_design_station_workflow.rules.json](./29_design_station_workflow.rules.json)

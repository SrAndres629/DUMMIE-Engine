---
spec_id: "DE-V2-L6-30"
title: "Visualizador Topológico 4D (Microservicio)"
status: "ACTIVE"
version: "1.0.0"
layer: "L6"
namespace: "io.dummie.v2.skin"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L6-13"
    relationship: "REFINES"
tags: ["cognitive_core", "telemetry_layer", "industrial_sdd"]
---

# Visualizador Topológico 4D (Microservicio)

## Abstract
Esta especificación define la capa de observación y visualización (Skin L6) del Agentic OS. Layer 6 (Tauri/React) actúa como el nervio óptico del sistema, traduciendo la telemetría binaria y causal en una interfaz visual (Command Canvas) para la supervisión humana.

## 1. Alcance de la Telemetría
El sistema captura trazas distribuidas (OpenTelemetry) y estados térmicos de los nodos, proyectándolos en un entorno 4D que respeta la flecha del tiempo de Lamport.

---

## [MSA] Sibling Components
- **Executable Contract**: 30_visualizer_microservice.feature
- **Machine Rules**: 30_visualizer_microservice.rules.json

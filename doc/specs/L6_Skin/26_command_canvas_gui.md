---
spec_id: "DE-V2-L6-26"
title: "Interfaz Command Canvas (GUI)"
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

# Interfaz Command Canvas (GUI)

## Abstract
Esta especificación define la capa de observación y visualización (Skin L6) del Agentic OS. Layer 6 (Tauri/React) actúa como el nervio óptico del sistema, traduciendo la telemetría binaria y causal en una interfaz visual (Command Canvas) para la supervisión humana.

## 1. Alcance de la Telemetría
El sistema captura trazas distribuidas (OpenTelemetry) y estados térmicos de los nodos, proyectándolos en un entorno 4D que respeta la flecha del tiempo de Lamport.

---

## 2. Modo Embebido (VS Code Webview)
Para lograr una paridad total con la experiencia de **Claw Code**, el Command Canvas soporta un modo de despliegue embebido:

- **Target**: Compilación React optimizada para el entorno restrictivo de extensiones de VS Code.
- **Bridge**: Comunicación mediante `postMessage` mapeada a los eventos de NATS/WebSocket de la SFE.
- **Context Sync**: El Webview se suscribe automáticamente a los eventos del **Semantic Bridge (Spec 49)** para mostrar diffs y ASTs en tiempo real dentro del Canvas.

Para los detalles técnicos de los límites de renderizado y el puente de comunicación, consulte el archivo de reglas [26_command_canvas_gui.rules.json](26_command_canvas_gui.rules.json).

---

## [MSA] Sibling Components
- **Executable Contract**: 26_command_canvas_gui.feature
- **Machine Rules**: 26_command_canvas_gui.rules.json

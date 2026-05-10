---
spec_id: "DE-V2-L6-26"
title: "Interfaz Command Canvas (GUI)"
status: "ACTIVE"
version: "2.2.0"
layer: "L6"
namespace: "io.dummie.v2.skin"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L6-13"
    relationship: "VISUALIZES"
  - id: "DE-V2-L4-49"
    relationship: "CONSUMES_CONTEXT"
tags: ["cognitive_core", "telemetry_layer", "industrial_sdd"]
---

# 26. Interfaz Command Canvas (GUI)

## Abstract
El **Command Canvas** es la interfaz gráfica maestra de Layer 6. Implementada en Tauri/React, esta GUI proporciona una representación visual en tiempo real de las operaciones del enjambre, permitiendo al PAH supervisar la salud de los nodos, auditar los parches quirúrgicos y gestionar la evolución arquitectónica del monorepo mediante una experiencia de usuario premium e industrial.

## 1. Cognitive Context Model (Ref)
Para los límites de comunicación del puente (VS Code Webview), la política de seguridad `postMessage` y los requisitos de RPC Timeout, consulte el archivo hermano [26_command_canvas_gui.rules.json](./26_command_canvas_gui.rules.json).

---

## 2. Modo Embebido (VS Code Integration)
El Command Canvas soporta una integración profunda con el IDE:
- **VS Code Webview:** Despliegue optimizado para funcionar dentro del ecosistema de VS Code como una extensión de control soberano.
- **Bi-directional Bridge:** Comunicación segura mediante un puente de mensajes que mapea los eventos del sistema nervioso (L1) a la UI.
- **Context Synchronization:** Visualización instantánea de los datos del Semantic Bridge ([Spec 49](../L4_Edge/49_lsp_context_hydration_protocol.md)), incluyendo diffs, diagnósticos y la estructura del LST.

---

## 3. Visualización y Control
La GUI ofrece herramientas de mando y control:
1.  **Node Topology:** Mapa interactivo de la salud y carga de los nodos en Layer 5.
2.  **Surgical Diff Viewer:** Interfaz de revisión para parches propuestos antes de su cristalización física.
3.  **Audit Ledger View:** Acceso visual al registro de decisiones ([Spec 34](../L2_Brain/34_decision_ledger_auditor.md)) con filtrado por causalidad y tiempo de Lamport.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [26_command_canvas_gui.feature](./26_command_canvas_gui.feature)
- **Machine Rules:** [26_command_canvas_gui.rules.json](./26_command_canvas_gui.rules.json)

---
spec_id: "DE-V2-L6-30"
title: "Visualizador Topológico 4D (Microservicio)"
status: "ACTIVE"
version: "2.2.0"
layer: "L6"
namespace: "io.dummie.v2.skin"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L6-13"
    relationship: "EXTENDS"
tags: ["cognitive_core", "telemetry_layer", "industrial_sdd"]
---

# 30. Visualizador Topológico 4D (Microservicio)

## Abstract
El **Visualizador Topológico 4D** es el motor de renderizado de Layer 6. Este microservicio se encarga de transformar los flujos de telemetría y las estructuras del LST en representaciones gráficas interactivas. Utilizando motores de grafos 3D (React Three Fiber), el sistema proyecta la topología del enjambre, permitiendo una navegación espacial y temporal por el conocimiento y la infraestructura de fabricación.

## 1. Cognitive Context Model (Ref)
Para los motores visuales soportados (Force Directed 3D), la fuente de telemetría (NATS) y los requisitos de sincronización en tiempo real, consulte el archivo hermano [30_visualizer_microservice.rules.json](./30_visualizer_microservice.rules.json).

---

## 2. Proyección Espacial
El Visualizador transforma datos abstractos en geometría:
- **LST Projection:** Representación del árbol semántico del monorepo como un bosque de nodos interconectados.
- **Topology Mapping:** Visualización física de los nodos de Layer 5, indicando su estado de salud, carga SIMD y temperatura.
- **Temporal Scrubbing:** Capacidad de "rebobinar" el estado del sistema visualmente para auditar el historial de transformaciones.

---

## 3. Invariantes de Interfaz
El microservicio garantiza la fidelidad visual:
1.  **Direct Telemetry Link:** Suscripción directa a los buses de datos NATS para evitar latencias en la actualización del estado visual.
2.  **State Consistency:** La UI debe reflejar fielmente el estado ontológico reportado por el Cerebro L2; cualquier discrepancia visual se marca como un error de sincronización.
3.  **Human Authority:** Las acciones destructivas iniciadas desde el Visualizador (ej. Apoptosis de un nodo) requieren la aprobación explícita y soberana del PAH.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [30_visualizer_microservice.feature](./30_visualizer_microservice.feature)
- **Machine Rules:** [30_visualizer_microservice.rules.json](./30_visualizer_microservice.rules.json)

---
spec_id: "DE-V2-L6-13"
title: "Observabilidad Sistémica (OpenTelemetry)"
status: "ACTIVE"
version: "2.2.0"
layer: "L6"
namespace: "io.dummie.v2.skin"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L1-41"
    relationship: "CONSUMES_VIA"
tags: ["cognitive_core", "telemetry_layer", "industrial_sdd"]
---

# 13. Observabilidad Sistémica (OpenTelemetry)

## Abstract
La **Observabilidad Sistémica** es la ventana del PAH hacia el interior del enjambre. Utilizando el estándar OpenTelemetry, Layer 6 (Tauri) captura y visualiza trazas distribuidas, logs y métricas de rendimiento de todas las capas. Este componente garantiza la transparencia total de la fabricación de software, permitiendo auditar cada decisión agéntica en una línea de tiempo coherente basada en relojes de Lamport.

## 1. Cognitive Context Model (Ref)
Para la capa del recolector (L1), el backend de almacenamiento (Redb) y las cabeceras de propagación de trazas (Trace ID, Span ID, Lamport Tick), consulte el archivo hermano [13_observability_opentelemetry.rules.json](./13_observability_opentelemetry.rules.json).

---

## 2. Telemetría Distribuida
El sistema instrumenta cada interacción entre capas:
- **Causal Tracing:** Seguimiento de la cadena de razonamiento desde el `Intent` original hasta la ejecución física del parche.
- **Lamport Timestamps:** Sincronización lógica de eventos en un sistema distribuido, asegurando que la flecha del tiempo sea consistente en el Visualizer.
- **Resource Monitoring:** Captura de estados térmicos y de memoria de los nodos en Layer 5 para su representación visual.

---

## 3. Invariantes de Observación
La transparencia es un requisito ineludible:
1.  **No Silence Policy:** El sistema prohíbe silenciar alertas críticas de seguridad o de drift arquitectónico.
2.  **Atomic Propagation:** Las trazas deben propagarse a través de todas las capas; una acción sin traza de origen es considerada una intrusión y bloqueada por el Escudo L3.
3.  **Real-time Visualization:** La latencia entre la generación del evento y su aparición en el Command Canvas debe ser mínima para permitir una intervención humana efectiva.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [13_observability_opentelemetry.feature](./13_observability_opentelemetry.feature)
- **Machine Rules:** [13_observability_opentelemetry.rules.json](./13_observability_opentelemetry.rules.json)

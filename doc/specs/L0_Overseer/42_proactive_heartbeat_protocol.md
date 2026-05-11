---
spec_id: "DE-V2-L0-42"
title: "Protocolo de Heartbeat Proactivo (The Pulse)"
status: "ACTIVE"
version: "2.2.0"
layer: "L0"
namespace: "io.dummie.v2.orchestration.proactive"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-05"
    relationship: "EXTENDS"
  - id: "DE-V2-L1-41"
    relationship: "USES_WIRE"
tags: ["proactive_autonomy", "heartbeat", "elixir_otp", "claw_ism"]
---

# 42. Protocolo de Heartbeat Proactivo (The Pulse)

## Abstract
DUMMIE Engine trasciende el modelo reactivo mediante el **Protocolo de Heartbeat Proactivo**. El sistema se dota de capacidad de **Despertar Autónomo**, donde el Overseer (L0) orquesta auditorías y reflexiones automáticas basadas en el entorno físico y cognitivo, sin requerir intervención humana constante.

## 1. Cognitive Context Model (Ref)
Para los mecanismos de disparo (GenServer), el formato de señal NATS y las restricciones de tareas proactivas (Límite de Profundidad), consulte el archivo hermano [42_proactive_heartbeat_protocol.rules.json](./42_proactive_heartbeat_protocol.rules.json).

---

## 2. El Ciclo de Vida del Pulso (The Pulse)
El Overseer (L0) mantiene un proceso `PulseDaemon` (GenServer) que rige la proactividad del enjambre:

1.  **Tick Generation:** Emisión de señal `pulse` a través del bus NATS en intervalos regulares.
2.  **LST Context Injection:** Inyección del contenido de `doc/HEARTBEAT.md` en el contexto de los agentes L2.
3.  **Autonomous Reasoning:** Análisis de tareas pendientes y cambios en el monorepo (L4 Zig).
4.  **Action Proposal:** Generación de un `Intent` para ejecución tras validación de consenso.

---

## 3. Contrato de HEARTBEAT.md
El archivo `doc/HEARTBEAT.md` actúa como la **Memoria de Intenciones Proactivas**. Es un SSoT mutable que el agente audita en cada Pulso.

### 3.1 Secciones Obligatorias
- **## Daily Recurring Tasks:** Tareas de mantenimiento e integridad SDD.
- **## Background Monitors:** Vigilancia de repositorios y servicios externos.
- **## Pending Reflections:** Ambigüedades de diseño y mejoras ontológicas.

---

## 4. Invariante de Red: Protección del Multiverso
Para evitar bucles de autorreferencia infinitos:
- **Depth Limit:** Las tareas iniciadas por un `pulse` no pueden generar otros `pulses` (Depth = 0).
- **Budget Control:** Consumo limitado por el E-Shield ([Spec 14](14_value_engineering_and_governance.md)) al 15% del presupuesto diario.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [42_proactive_heartbeat_protocol.feature](./42_proactive_heartbeat_protocol.feature)
- **Machine Rules:** [42_proactive_heartbeat_protocol.rules.json](./42_proactive_heartbeat_protocol.rules.json)

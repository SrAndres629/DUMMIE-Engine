---
spec_id: "DE-V2-L0-42"
title: "Protocolo de Heartbeat Proactivo (The Pulse)"
status: "ACTIVE"
version: "1.0.0"
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
Inspirado por el patrón de **OpenClaw**, esta especificación dota al Agentic OS de una capacidad de **Despertar Autónomo**. El sistema pasa de ser una herramienta reactiva a un agente proactivo que se audita a sí mismo y a su entorno sin necesidad de intervención humana constante.

## 1. Cognitive Context Model (JSON)
```json
{
  "trigger_mechanism": {
    "type": "GenServer Timer",
    "default_interval": "1800s",
    "jitter_pct": 0.1
  },
  "signal": {
    "subject": "ao.v2.l0.signal.pulse",
    "payload": "PulseEvent",
    "priority": "LOW"
  },
  "sources": [
    "doc/HEARTBEAT.md",
    "governance/rules/cron_schedules.json"
  ],
  "constraints": {
    "max_autonomous_tasks_per_pulse": 3,
    "thermal_override": true
  },
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. El Ciclo de Vida del Pulso (The Pulse)
El Overseer (L0) mantiene un proceso `PulseDaemon` (GenServer) que rige la proactividad del enjambre:

1.  **Tick Generation:** Cada 30 minutos (configurable), el `PulseDaemon` emite una señal a través del bus NATS.
2.  **LST Context Injection:** La señal `pulse` inyecta el contenido de `doc/HEARTBEAT.md` directamente en el contexto de los agentes L2 (Brain) registrados.
3.  **Autonomous Reasoning:** El cerebro L2 analiza las tareas pendientes en el heartbeat y los cambios detectados en el monorepo (L4 Zig scanning).
4.  **Action Proposal:** Si se identifica una tarea prioritaria, el agente genera un `Intent` ([Spec 05](05_orchestration_stack_and_glue.md)) para su ejecución.

---

## 3. Contrato de HEARTBEAT.md
El archivo `doc/HEARTBEAT.md` actúa como la **Memoria de Intenciones Proactivas**. Sigue un formato Markdown estricto que el agente puede leer y escribir.

### 3.1 Secciones Obligatorias
- **## Daily Recurring Tasks:** Tareas que se ejecutan una vez al día (ej. "Limpiar logs", "Validar integridad SDD").
- **## Background Monitors:** Servicios o repositorios que el agente debe vigilar.
- **## Pending Reflections:** Dudas de arquitectura o ambigüedades que el agente debe pensar "en su tiempo libre".

---

## 4. Invariante de Red: Protección del Multiverso
Para evitar que el sistema entre en bucles de autorreferencia infinitos:
- **Depth Limit:** Las tareas iniciadas por un `pulse` no pueden generar otros `pulses` con una profundidad >1.
- **Budget Control:** El consumo de tokens de las tareas proactivas está limitado por el E-Shield ([Spec 14](14_value_engineering_and_governance.md)) a un máximo del 15% del presupuesto diario.

---

## 5. Acceptance Criteria (BDD)

### Feature: Proactive Pulse Triggering
  Scenario: Overseer triggers a pulse
    Given a configured interval of "1800s"
    When the PulseDaemon timer expires
    Then a "PulseEvent" must be broadcasted to "ao.v2.l0.signal.pulse"
    And L2 Brain units must receive the "HEARTBEAT.md" context.

  Scenario: Brain ignores pulse due to thermal throttling
    Given the RTX 3060 TDP is at "170W"
    When the "PulseEvent" is received
    Then L2 Brain must defer processing until thermal baseline is recovered
    And the deferral must be recorded in the Session Ledger.

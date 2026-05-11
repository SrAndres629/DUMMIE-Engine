---
spec_id: "DE-V2-L2-37"
title: "Protocolo de Descubrimiento Agent-to-Agent (A2A)"
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

# 37. Protocolo de Descubrimiento Agent-to-Agent (A2A)

## Abstract
El Protocolo A2A permite la colaboración dinámica entre agentes especializados dentro del Swarm. Define la gramática para que un agente solicite asistencia, delegue tareas o descubra capacidades funcionales de otros agentes en tiempo real, garantizando que el orquestador cognitivo pueda escalar horizontalmente sin perder la coherencia del diseño global.

## 1. Cognitive Context Model (Ref)
Para el tópico de descubrimiento en NATS, los requisitos de handshake y los límites de saltos de descubrimiento (Discovery Hops), consulte el archivo hermano [37_a2a_discovery_protocol.rules.json](./37_a2a_discovery_protocol.rules.json).

---

## 2. Presencia y Capacidades
Los agentes anuncian su presencia y expertise mediante latidos (Heartbeats) en el bus de datos:
- **Expertise Tags:** Lista de habilidades registradas ([Spec 28](28_skill_standard_yaml.md)).
- **Current Load:** Nivel de saturación cognitiva para balanceo de carga.
- **Authority Level:** Rango de decisión delegado por Layer 0.

---

## 3. Delegación Segura
La transferencia de tareas entre agentes sigue un protocolo de delegación:
1.  **Request:** Solicitud formal de capacidad.
2.  **Handshake:** Validación de permisos y disponibilidad.
3.  **Context Transfer:** Envío de los vectores de memoria relevantes (6D-Context) para asegurar la continuidad del razonamiento.
4.  **Result Integration:** El agente original integra el resultado y lo valida contra el ledger de sesión.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [37_a2a_discovery_protocol.feature](./37_a2a_discovery_protocol.feature)
- **Machine Rules:** [37_a2a_discovery_protocol.rules.json](./37_a2a_discovery_protocol.rules.json)

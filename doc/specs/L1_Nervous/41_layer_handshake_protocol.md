---
spec_id: "DE-V2-L1-41"
title: "Protocolo de Handshake y Mensajería (The Wire)"
status: "ACTIVE"
version: "2.2.0"
layer: "L1"
namespace: "io.dummie.v2.wire"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L1-10"
    relationship: "REQUIRES"
  - id: "DE-V2-L5-16"
    relationship: "REFINES"
tags: ["connectivity", "nats", "shm", "binary_contract"]
---

# 41. Protocolo de Handshake y Mensajería (The Wire)

## Abstract
Esta especificación define el **Tejido Conectivo** (The Wire) del Agentic OS. Establece la gramática de los tópicos NATS, los offsets del bus de memoria compartida (SHM) y el protocolo de negociación inicial (Handshake) para garantizar un determinismo total en la comunicación políglota entre las capas del sistema.

## 1. Cognitive Context Model (Ref)
Para la configuración de NATS (JetStream), los esquemas de envoltorio JSON-RPC (ACP) y los invariantes de versión de protocolo, consulte el archivo hermano [41_layer_handshake_protocol.rules.json](./41_layer_handshake_protocol.rules.json).

---

## 2. Topología de Red y Memoria
El sistema opera sobre un plano de control basado en NATS y un plano de datos de latencia ultra-baja mediante Memoria Compartida (SHM) utilizando Apache Arrow. 

---

## 3. Alineación con ACP (Agent Client Protocol)
Para integrarse con el ecosistema de IDEs modernos, el sistema nervioso implementa un puente de compatibilidad con **ACP**:
- **Protocolo**: Envoltorio JSON-RPC sobre el bus NATS.
- **Tipos de Mensajes**: Soporte nativo para `agent/initialize`, `textDocument/didOpen`, y `context/hydrate`.
- **Determinismo**: Mapeo de mensajes ACP a `Intent` de Protobuf para auditoría en el Escudo L3.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [41_layer_handshake_protocol.feature](./41_layer_handshake_protocol.feature)
- **Machine Rules:** [41_layer_handshake_protocol.rules.json](./41_layer_handshake_protocol.rules.json)

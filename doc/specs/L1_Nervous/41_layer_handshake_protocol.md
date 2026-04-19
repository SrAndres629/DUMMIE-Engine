---
spec_id: "DE-V2-L1-41"
title: "Protocolo de Handshake y Mensajería (The Wire)"
status: "ACTIVE"
version: "1.0.0"
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
Esta especificación define el **Tejido Conectivo** (The Wire) del Agentic OS. Establece la gramática exacta de los tópicos NATS, los offsets binarios del bus de memoria compartida (SHM) y el protocolo de negociación inicial entre capas (Handshake) para garantizar un determinismo total en la comunicación políglota.

## 1. Topología de Red y Memoria
El sistema opera sobre un plano de control basado en NATS (JetStream) y un plano de datos de latencia ultra-baja mediante Memoria Compartida (SHM) utilizando el formato Apache Arrow. 

---

## 2. Alineación con ACP (Agent Client Protocol)
Para integrarse profundamente con el ecosistema de IDEs modernos (especialmente VS Code/Claw), el sistema nervioso implementa un puente de compatibilidad con **ACP**:

- **Protocolo**: Envoltorio JSON-RPC sobre el bus NATS.
- **Tipos de Mensajes**: Soporte nativo para `agent/initialize`, `textDocument/didOpen`, y `context/hydrate`.
- **Determinismo**: Cada mensaje ACP se mapea a un `Intent` de Protobuf, garantizando que el Escudo L3 pueda auditar las órdenes del IDE antes de que lleguen al Cerebro.

Para los detalles técnicos de los esquemas JSON-RPC y los envoltorios binarios, consulte el archivo de reglas [41_layer_handshake_protocol.rules.json](41_layer_handshake_protocol.rules.json).


## [MSA] Sibling Components
- **Executable Contract**: [41_layer_handshake_protocol.feature](41_layer_handshake_protocol.feature)
- **Machine Rules**: [41_layer_handshake_protocol.rules.json](41_layer_handshake_protocol.rules.json)

---
spec_id: "DE-V2-L1-10"
title: "Contratos Protobuf (Ley de Schema-First)"
status: "ACTIVE"
version: "2.2.0"
layer: "L1"
namespace: "io.dummie.v2.contracts"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-03"
    relationship: "IMPLEMENTS"
tags: ["cognitive_core", "protobuf_contracts", "industrial_sdd"]
---

# 10. Contratos Protobuf (Ley de Schema-First)

## Abstract
La comunicación entre capas cognitivas se rige por la **Ley de Schema-First**. Esta especificación define los contratos técnicos ineludibles para la orquestación políglota, el manejo de errores distribuido y el control de acceso soberano en el Agentic OS.

## 1. Cognitive Context Model (Ref)
Para los mensajes requeridos (PhaseTransition, PolyglotError), los tiempos de espera RPC y los invariantes de alineación de memoria (SHM), consulte el archivo hermano [10_protobuf_contracts.rules.json](./10_protobuf_contracts.rules.json).

---

## 2. Filosofía de Contratos
Toda interacción en el Agentic OS debe estar precedida por un esquema Protobuf validado. Esto garantiza que lenguajes tan dispares como Elixir, Go, Python y Rust hablen el mismo idioma tipado. Los contratos actúan como la **Verdad Lógica** del sistema.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [10_protobuf_contracts.feature](./10_protobuf_contracts.feature)
- **Machine Rules:** [10_protobuf_contracts.rules.json](./10_protobuf_contracts.rules.json)

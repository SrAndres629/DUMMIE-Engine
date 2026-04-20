---
spec_id: "DE-V2-L1-11"
title: "Protocolo de Plano de Datos (Apache Arrow Zero-Copy)"
status: "ACTIVE"
version: "1.0.0"
layer: "L1"
namespace: "io.dummie.v2.dataplane"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-01"
    relationship: "REFINES"
tags: ["data_plane", "zero_copy", "apache_arrow"]
---

# 11. Protocolo de Plano de Datos (Apache Arrow)

## 1. Estructura del RecordBatch (Logical Layout)
Para garantizar la interoperabilidad entre Go, Python y Zig, todo `RecordBatch` que circule por la memoria compartida (SHM) debe seguir este esquema:

| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `event_id` | utf8 (UUID) | Identificador único de la transacción causal. |
| `lamport_tick` | uint64 | Tiempo lógico asignado por el TimeKeeper (L1). |
| `layer_source` | int8 (Enum) | Capa que originó el dato (0-6). |
| `payload_type` | utf8 | "LST_NODE", "COGNITIVE_STEP", "TELEMETRY". |
| `payload_blob` | binary | Datos serializados (FlatBuffers) según el tipo. |

## 2. Invariante de Acceso
Solo la Capa L1 (Nervous) puede incrementar el `lamport_tick`. Las demás capas actúan como lectores o escritores de estados, pero nunca como árbitros del tiempo.

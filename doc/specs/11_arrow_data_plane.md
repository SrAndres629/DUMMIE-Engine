---
spec_id: "DE-V2-L1-11"
title: "Protocolo de Plano de Datos (Apache Arrow Zero-Copy)"
status: "ACTIVE"
version: "2.2.0"
layer: "L1"
namespace: "io.dummie.v2.dataplane"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-03"
    relationship: "IMPLEMENTS"
tags: ["data_plane", "zero_copy", "apache_arrow"]
---

# 11. Protocolo de Plano de Datos (Apache Arrow)

## Abstract
Este protocolo define el intercambio masivo de información entre las capas del Agentic OS utilizando **Apache Arrow**. Se garantiza una transferencia de datos con latencia cero (Zero-Copy) mediante el uso de memoria compartida (SHM) y esquemas rígidos de `RecordBatch` para asegurar la interoperabilidad políglota de alto rendimiento.

## 1. Cognitive Context Model (Ref)
Para los esquemas de RecordBatch, los controles de acceso por capa (RW/R) y los invariantes de serialización binaria, consulte el archivo hermano [11_arrow_data_plane.rules.json](./11_arrow_data_plane.rules.json).

---

## 2. Estructura del RecordBatch (Logical Layout)
Para garantizar la interoperabilidad entre Go, Python y Zig, todo `RecordBatch` que circule por la memoria compartida (SHM) debe seguir este esquema:

| Campo | Tipo | Propósito |
| :--- | :--- | :--- |
| `event_id` | utf8 (UUID) | Identificador único de la transacción causal. |
| `lamport_tick` | uint64 | Tiempo lógico asignado por el TimeKeeper (L1). |
| `layer_source` | int8 (Enum) | Capa que originó el dato (0-6). |
| `payload_type` | utf8 | Categoría del dato (LST, Cognitive, Telemetry). |
| `payload_blob` | binary | Datos serializados (FlatBuffers) según el tipo. |

---

## 3. Invariante de Acceso y Tiempo
Solo la Capa L1 (Nervous) posee la autoridad para incrementar el `lamport_tick`. Las demás capas actúan como lectores o escritores de estados, pero nunca como árbitros de la causalidad temporal del sistema.

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [11_arrow_data_plane.feature](./11_arrow_data_plane.feature)
- **Machine Rules:** [11_arrow_data_plane.rules.json](./11_arrow_data_plane.rules.json)

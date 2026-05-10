---
spec_id: "DE-V2-L1-23"
title: "Nodos Atómicos y Modularidad Plug & Play"
status: "ACTIVE"
version: "2.2.0"
layer: "L1"
namespace: "io.dummie.v2.atoms"
authority: "ARCHITECT"
dependencies:
  - id: "DE-V2-L0-11"
    relationship: "REQUIRES"
tags: ["cognitive_core", "modular_nodes", "industrial_sdd"]
---

# 23. Nodos Atómicos y Modularidad Plug & Play

## Abstract
Para garantizar la inmunidad al acoplamiento accidental y facilitar la evolución del sistema, DUMMIE Engine define el **Nodo Atómico** como la unidad mínima de construcción funcional. Los nodos operan bajo el paradigma de Puertos y Adaptadores (Hexagonal), permitiendo el intercambio dinámico de implementaciones sin alterar la lógica de dominio.

## 1. Cognitive Context Model (Ref)
Para la arquitectura de estratos del nodo (Port, Core, Adapter, Shield), el esquema del manifiesto de nodo y los protocolos de Hot-Swapping bajo gobernanza de L0, consulte el archivo hermano [23_atomic_modular_nodes.rules.json](./23_atomic_modular_nodes.rules.json).

---

## 2. Anatomía del Nodo Atómico (Hexagonal)
Cada nodo se compone de cuatro estratos herméticamente aislados:
1. **Port (Definition):** Contrato abstracto definido en Protobuf ([Spec 10](10_protobuf_contracts.md)).
2. **Core (Domain):** Lógica de negocio pura sin dependencias externas.
3. **Adapter (Plug):** Implementación técnica específica (I/O).
4. **Shield (Security):** Inyección de reglas SDD mediante el motor de Rust (L3).

---

## 3. Protocolo de Intercambio Dinámico (Atomic Swap)
El sistema permite el **Hot-Swapping** de adaptadores bajo gobernanza de Layer 0 (Elixir):
- **Candidate Validation:** El Auditor (L2) verifica que el nuevo adaptador satisfaga el Port mediante escaneo LST (L4).
- **Consensus Commit:** Cambio de referencia en el contenedor de inyección de dependencias.
- **Rollback Safety:** Restauración inmediata ante fallo de tests Causal-Invariant.

---

## 4. Coreografía de Nodos
La comunicación entre nodos atómicos se realiza exclusivamente a través del **Bus de Datos (NATS/Arrow)**:
- **Zero-Copy Message Passing:** Compartición de punteros de memoria sin coste de serialización.
- **Topological Discovery:** Registro en el Palacio de Loci ([Spec 18](../L4_Edge/18_loci_ontology_mapping.md)) para consultas de grafo (GraphRAG).

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [23_atomic_modular_nodes.feature](./23_atomic_modular_nodes.feature)
- **Machine Rules:** [23_atomic_modular_nodes.rules.json](./23_atomic_modular_nodes.rules.json)

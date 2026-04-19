---
spec_id: "DE-V2-L1-23"
title: "Nodos Atómicos y Modularidad Plug & Play"
status: "ACTIVE"
version: "2.1.0"
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
Para garantizar la inmunidad al acoplamiento accidental y facilitar la evolución del sistema, DUMMIE Engine define el **Nodo Atómico** como la unidad mínima de construcción funcional. Los nodos operan bajo el paradigma de Puertos y Adaptadores, permitiendo el intercambio dinámico de implementaciones sin alterar la lógica de dominio.

## 1. Cognitive Context Model (JSON)
```json
{
  "node_architecture": {
    "strata": ["Port (Definition)", "Core (Domain)", "Adapter (Plug)", "Shield (Security)"],
    "pattern": "Ports & Adapters (Hexagonal)"
  },
  "manifest_schema": {
    "node_uid": "UUID-V4",
    "layer": "enum(L0..L6)",
    "interface": {"protobuf_svc": "string", "shm_req_size": "bytes"},
    "governance": {"authority_level": "enum", "sdd_rules": "array"}
  },
  "lifecycle": {
    "swap_protocol": "Atomic Swap via L0",
    "discovery": "NATS/Arrow Zero-Copy",
    "registry": "Loci Palace ([Spec 18](../L4_Edge/18_loci_ontology_mapping.md))"
  },
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. Anatomía del Nodo Atómico (manifest.json)
Cada unidad funcional se despliega con un manifiesto de metadatos obligatorio que rige su ciclo de vida:

```json
{
  "node_uid": "UUID-V4",
  "name": "L2_Brain_FeatureExtractor",
  "layer": "L2_Brain",
  "version": "1.0.4",
  "expertise_tags": ["LST-Scraping", "Logic-Audit"],
  "interface": {
    "protobuf_svc": "LociMapper.IndexFile",
    "shm_req_size": "256MB",
    "alignment": 64
  },
  "governance": {
    "authority_level": "AGENT_PROPOSAL",
    "sdd_rules": ["VIO_HEX_001", "RES_COG_001"]
  },
  "telemetry": "VERBOSE_CAUSAL"
}
```

Cada nodo se compone de cuatro estratos herméticamente aislados:
1. **Port (Definition):** Contrato abstracto definido en Protobuf ([Spec 10](10_protobuf_contracts.md)). Determina el "Qué" sin especificar el "Cómo".
2. **Core (Domain):** Lógica de negocio pura. No tiene dependencias externas (Specs 04/21).
3. **Adapter (Plug):** Implementación técnica específica. Es el único estrato que interactúa con I/O.
4. **Shield (Security):** Inyecta las reglas SDD del manifiesto mediante el motor de Rust (L3).

---

## 3. Protocolo de Intercambio Dinámico (Atomic Swap)
El sistema permite el **Hot-Swapping** de adaptadores bajo gobernanza de Layer 0 (Elixir):
- **Candidate Validation:** El Auditor (L2) verifica que el nuevo adaptador satisfaga el Port original mediante escaneo LST (L4).
- **Consensus Commit:** Cambio de referencia en el contenedor de inyección de dependencias.
- **Rollback Safety:** Si el nuevo nodo eleva la entropía o falla los tests Causal-Invariant, Elixir restaura el nodo anterior en milisegundos.

---

## 4. Coreografía de Nodos
La comunicación entre nodos atómicos se realiza exclusivamente a través del **Bus de Datos (NATS/Arrow)**:
- **Zero-Copy Message Passing:** Los nodos comparten punteros de memoria, eliminando el coste de serialización.
- **Topological Discovery:** Los nodos se registran en el Palacio de Loci ([Spec 18](../L4_Edge/18_loci_ontology_mapping.md)), permitiendo a los agentes encontrar capacidades funcionales mediante consultas de grafo (GraphRAG).

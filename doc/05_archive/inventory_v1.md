---
spec_id: "DE-V2-INDEX-01"
title: "Inventario de Entidades Heredadas (V1)"
status: "ACTIVE"
version: "2.2.0"
layer: "L0"
namespace: "io.dummie.v2.index"
authority: "LIBRARIAN"
dependencies:
  - id: "DE-V2-L0-06"
    relationship: "INFORMS"
tags: ["inventory", "legacy_migration", "industrial_sdd"]
---

# Inventario de Entidades Heredadas (V1)

## Abstract
Este documento sirve como el **Inventario de Referencia Lógica** para la migración Greenfield V2. Define las entidades, patrones y lógicas que deben ser re-manufacturadas bajo los nuevos contratos de soberanía. Como archivo de archivo, representa la "Memoria Genética" del sistema previo a su industrialización MSA V3.

## 1. Cognitive Context Model (Ref)
Para los mapas de migración inmutables, la hoja de ruta de traspasos y los invariantes de preservación histórica, consulte el archivo hermano [inventory_v1.rules.json](./inventory_v1.rules.json).

---

## 2. Núcleo Cognitivo (Brain V1)
| Entidad V1 | Rol Original | Destino en V2 | Invariante de Migración |
| :--- | :--- | :--- | :--- |
| `AgentOrchestrator` | Gestión de hilos Python. | [Layer 0 (Elixir)](../specs/L0_Overseer/03_polyglot_architecture.md) | Resiliencia OTP. |
| `TaskQueue` | Lista de tareas en memoria. | [Layer 1 (NATS)](../specs/L1_Nervous/10_protobuf_contracts.md) | Persistencia causal. |
| `ContextWindow` | Gestor de prompts. | [Layer 2 (LangGraph)](../specs/L0_Overseer/05_orchestration_stack_and_glue.md) | Aislamiento hexagonal. |

---

## 3. Persistencia y Memoria
| Entidad V1 | Rol Original | Destino en V2 | Invariante de Migración |
| :--- | :--- | :--- | :--- |
| `VectorDB_Wrapper` | Acceso a base de vectores. | [Layer 4 (KùzuDB)](../specs/L4_Edge/18_loci_ontology_mapping.md) | Mapeo topológico Loci. |
| `Shuttle_Service` | Intercambio de mensajes. | [Layer 1 (NATS/Arrow)](../specs/L1_Nervous/15_mcp_sidecar_isolation.md) | Zero-Copy. |

---

## 4. Seguridad y Validación
| Entidad V1 | Rol Original | Destino en V2 | Invariante de Migración |
| :--- | :--- | :--- | :--- |
| `SafetyCheck` | Reglas de validación manual. | [Layer 3 (Rust Shields)](../specs/L3_Shield/04_anti_ignorance_shields.md) | Validación física SDD. |
| `AuthToken` | Validación de usuario. | [PA_TOKEN](../specs/L0_Overseer/14_value_engineering_and_governance.md) | AuthorityLevel Protobuf. |

---

## [MSA] Sibling Components Requeridos
Todo documento maestro debe ir acompañado de sus archivos hermanos para convertirse en una *Active Architectural Fitness Function*:
- **Executable Contract:** [inventory_v1.feature](./inventory_v1.feature)
- **Machine Rules:** [inventory_v1.rules.json](./inventory_v1.rules.json)

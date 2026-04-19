---
spec_id: "DE-V2-INDEX-01"
title: "Inventario de Entidades Heredadas (V1)"
status: "ACTIVE"
version: "2.1.0"
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
Este documento sirve como el **Inventario de Referencia Lógica** para la migración Greenfield V2. Define las entidades, patrones y lógicas que deben ser re-manufacturadas bajo los nuevos contratos de soberanía.

## 1. Cognitive Context Model (JSON)
```json
{
  "migration_map": [
    {
      "source": "AgentOrchestrator",
      "target": "[L0 (Elixir)](../specs/L0_Overseer/03_polyglot_architecture.md)",
      "invariant": "OTP Resilience"
    },
    {
      "source": "TaskQueue",
      "target": "[L1 (NATS)](../specs/L0_Overseer/05_orchestration_stack_and_glue.md)",
      "invariant": "Causal Persistence"
    },
    {
      "source": "VectorDB",
      "target": "[L4 (KùzuDB)](../specs/L4_Edge/18_loci_ontology_mapping.md)",
      "invariant": "Loci Topology"
    }
  ],
  "roadmap": [
    "[Scraping to L4 (Zig)](../specs/L4_Edge/18_loci_ontology_mapping.md)",
    "[Prompt Gen to L2/L5](../specs/L2_Brain/21_software_fabrication_engine.md)",
    "[Visualization to L6 (Tauri)](../specs/L6_Skin/17_optical_nerve_telemetry.md)"
  ],
  "personality_ref": "[DE-V2-L0-33](../specs/L0_Overseer/33_persistent_personality_mood.md)",
  "ledger_link": "[DE-V2-L2-34](../specs/L2_Brain/34_decision_ledger_auditor.md)"
}
```

---

## 2. Núcleo Cognitivo (Brain V1)
| Entidad V1 | Rol Original | Destino en V2 | Invariante de Migración |
| :--- | :--- | :--- | :--- |
| `AgentOrchestrator` | Gestión de hilos Python. | [Layer 0 (Elixir)](../specs/L0_Overseer/03_polyglot_architecture.md) | Debe ser un proceso resiliente (OTP). |
| `TaskQueue` | Lista de tareas en memoria. | [Layer 1 (NATS)](../specs/L1_Nervous/10_protobuf_contracts.md) | Persistencia causal absoluta. |
| `ContextWindow` | Gestor de prompts. | [Layer 2 (LangGraph)](../specs/L0_Overseer/05_orchestration_stack_and_glue.md) | Aislamiento hexagonal estricto. |

---

## 3. Persistencia y Memoria
| Entidad V1 | Rol Original | Destino en V2 | Invariante de Migración |
| :--- | :--- | :--- | :--- |
| `VectorDB_Wrapper` | Acceso a base de vectores. | [Layer 4 (KùzuDB)](../specs/L4_Edge/18_loci_ontology_mapping.md) | Mapeo topológico mediante Palacio de Loci. |
| `Shuttle_Service` | Intercambio de mensajes. | [Layer 1 (NATS/Arrow)](../specs/L1_Nervous/15_mcp_sidecar_isolation.md) | Eliminación de copias físicas (Zero-Copy). |

---

## 4. Seguridad y Validación
| Entidad V1 | Rol Original | Destino en V2 | Invariante de Migración |
| :--- | :--- | :--- | :--- |
| `SafetyCheck` | Reglas de validación manual. | [Layer 3 (Rust Shields)](../specs/L3_Shield/04_anti_ignorance_shields.md) | Validación física mediante SDD ([Spec 22](../specs/L3_Shield/22_sdd_executable_contracts.md)). |
| `AuthToken` | Validación de usuario. | [PA_TOKEN](../specs/L0_Overseer/14_value_engineering_and_governance.md) (Governance) | Basado en AuthorityLevel de Protobuf. |

---

## 5. Próximos Traspasos (Hoja de Ruta)
1.  **Módulo de Scraping:** Migrar a [Layer 4 (Zig)](../specs/L4_Edge/25_blueprint_registry.md) para alta velocidad de ingesta.
2.  **Generador de Prompts:** Migrar a [Layer 2 (Mojo/Python)](../specs/L5_Muscle/20_simd_muscle_processing.md) para optimización SIMD.
3.  **Visualizador de Trazas:** Migrar a [Layer 6 (Tauri/TS)](../specs/L6_Skin/30_visualizer_microservice.md) para renderizado 4D.

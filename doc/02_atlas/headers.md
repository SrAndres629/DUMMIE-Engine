---
spec_id: "DE-V2-INDEX-00"
title: "Project Headers Index"
status: "ACTIVE"
version: "2.1.0"
layer: "L0"
namespace: "io.dummie.v2.index"
authority: "LIBRARIAN"
dependencies: []
tags: ["index", "metadata", "industrial_sdd"]
---

# Project Headers Index

## Abstract
Este documento actúa como el índice maestro de todas las especificaciones, decisiones arquitectónicas y manifiestos del proyecto DUMMIE Engine. Proporciona una visión rápida de la estructura cognitiva y técnica del sistema.

## 1. Cognitive Context Model (JSON)
```json
{
  "categories": [
    "Governance",
    "Brain",
    "Shield",
    "Nervous",
    "Muscle",
    "Skin",
    "Edge"
  ],
  "total_specs": 40,
  "total_adrs": 5,
  "validation": "SDD V3 Standard",
  "personality_ref": "DE-V2-L0-33",
  "ledger_link": "DE-V2-L2-34"
}
```

---

## 2. Core Specifications (L0-L6)

| ID | Title | Layer | Namespace |
| :--- | :--- | :--- | :--- |
| DE-V2-L0-00 | [Topology Tracker](../specs/L0_Overseer/00_topology_tracker.md) | L0 | .tracker |
| DE-V2-L5-01 | [Environment & Metal](../specs/L5_Muscle/01_environment_and_hardware.md) | L5 | .hardware |
| DE-V2-L2-02 | [Memory Engine (4D-TES)](../specs/L2_Brain/02_memory_engine_4d_tes.md) | L2 | .brain.memory |
| DE-V2-L0-03 | [Polyglot Architecture](../specs/L0_Overseer/03_polyglot_architecture.md) | L0 | .architecture |
| DE-V2-L3-04 | [Anti-Ignorance Shields](../specs/L3_Shield/04_anti_ignorance_shields.md) | L3 | .shield |
| DE-V2-L0-05 | [Orchestration Stack](../specs/L0_Overseer/05_orchestration_stack_and_glue.md) | L0 | .orchestrator |
| DE-V2-L0-06 | [Migration Strategy](../specs/L0_Overseer/06_migration_and_implementation_strategy.md) | L0 | .strategy |
| DE-V2-L0-07 | [Unknown Unknowns](../specs/L0_Overseer/07_unknown_unknowns_resolutions.md) | L0 | .resilience |
| DE-V2-L0-08 | [DevEx & Deployment](../specs/L0_Overseer/08_devex_and_deployment_strategy.md) | L0 | .devex |
| DE-V2-L2-09 | [4D-TES Annex](../specs/L2_Brain/09_annex_4d_tes_comparison.md) | L2 | .concepts |
| DE-V2-L1-10 | [Protobuf Contracts](../specs/L1_Nervous/10_protobuf_contracts.md) | L1 | .contracts |
| DE-V2-L0-11 | [Monorepo Structure](../specs/L0_Overseer/11_monorepo_structure.md) | L0 | .structure |
| DE-V2-L2-12 | [6D-Context Model](../specs/L2_Brain/12_6d_context_model.md) | L2 | .brain.context |
| DE-V2-L6-13 | [Observability (OTel)](../specs/L6_Skin/13_observability_opentelemetry.md) | L6 | .observability |
| DE-V2-L0-14 | [Value Engineering](../specs/L0_Overseer/14_value_engineering_and_governance.md) | L0 | .value_engineering |
| DE-V2-L1-15 | [I/O Isolation (FEI)](../specs/L1_Nervous/15_mcp_sidecar_isolation.md) | L1 | .io |
| DE-V2-L5-16 | [IPC Stability](../specs/L5_Muscle/16_hardware_ipc_stability.md) | L5 | .hardware |
| DE-V2-L6-17 | [Optical Nerve](../specs/L6_Skin/17_optical_nerve_telemetry.md) | L6 | .visualizer |
| DE-V2-L4-18 | [Loci Ontology](../specs/L4_Edge/18_loci_ontology_mapping.md) | L4 | .loci |
| DE-V2-L5-20 | [SIMD Muscle (Mojo)](../specs/L5_Muscle/20_simd_muscle_processing.md) | L5 | .muscle |
| DE-V2-L2-21 | [Fabrication Engine](../specs/L2_Brain/21_software_fabrication_engine.md) | L2 | .sfe |
| DE-V2-L3-22 | [Executable Contracts](../specs/L3_Shield/22_sdd_executable_contracts.md) | L3 | .shield.contracts |
| DE-V2-L1-23 | [Atomic Nodes](../specs/L1_Nervous/23_atomic_modular_nodes.md) | L1 | .atoms |
| DE-V2-L3-24 | [Legal Shield](../specs/L3_Shield/24_legal_compliance_shield.md) | L3 | .compliance |
| DE-V2-L4-25 | [Blueprint Registry](../specs/L4_Edge/25_blueprint_registry.md) | L4 | .blueprints |
| DE-V2-L6-26 | [Command Canvas (GUI)](../specs/L6_Skin/26_command_canvas_gui.md) | L6 | .gui.canvas |
| DE-V2-L2-27 | [Kaizen Loop](../specs/L2_Brain/27_kaizen_loop_refinement.md) | L2 | .kaizen |
| DE-V2-L2-28 | [Skill Standard](../specs/L2_Brain/28_skill_standard_yaml.md) | L2 | .skills |
| DE-V2-L2-29 | [Design Station](../specs/L2_Brain/29_design_station_workflow.md) | L2 | .workflow.design |
| DE-V2-L6-30 | [Visualizer Microservice](../specs/L6_Skin/30_visualizer_microservice.md) | L6 | .visualizer.svc |
| DE-V2-L2-31 | [Impact Analytics](../specs/L2_Brain/31_impact_analytics_blast_radius.md) | L2 | .analytics |
| DE-V2-L5-32 | [Multiverse Compression](../specs/L5_Muscle/32_multiverse_compression_necro_learning.md) | L5 | .compression |
| DE-V2-L0-33 | [Project Personality](../specs/L0_Overseer/33_persistent_personality_mood.md) | L0 | .personality |
| DE-V2-L2-34 | [Decision Ledger](../specs/L2_Brain/34_decision_ledger_auditor.md) | L2 | .governance.ledger |
| DE-V2-L5-35 | [Necro-Learning](../specs/L5_Muscle/35_necro_learning_pipeline.md) | L5 | .necro |
| DE-V2-L2-36 | [Cognitive Memory](../specs/L2_Brain/36_cognitive_memory_session_ledger.md) | L2 | .memory.session |
| DE-V2-L2-37 | [A2A Discovery](../specs/L2_Brain/37_a2a_discovery_protocol.md) | L2 | .cognitive.a2a |
| DE-V2-L2-38 | [Procedural Memory](../specs/L2_Brain/38_procedural_memory_crystallization.md) | L2 | .cognitive.memory.procedural |
| DE-V2-L2-39 | [Semantic Consistency](../specs/L2_Brain/39_semantic_consistency_agent.md) | L2 | .cognitive.sync |
| DE-V2-L4-40 | [Self-Healing](../specs/L4_Edge/40_self_healing_remediation_loop.md) | L4 | .infrastructure.healing |
| DE-V2-L0-49 | [Cognitive Closure (SCCP)](../specs/L0_Overseer/49_sovereign_cognitive_closure_protocol.md) | L0 | .governance.closure |

---

## 3. ADRs & Manifestos

| ID | Title | Layer | Status |
| :--- | :--- | :--- | :--- |
| DE-V2-GOV-01 | [Vision Manifesto](../00_foundation/vision_manifesto.md) | L0 | ACTIVE |
| DE-V2-GOV-02 | [C4 Model Graphs](../01_architecture/diagrams/c4_model_graphs.md) | L0 | ACTIVE |
| DE-V2-ADR-001 | [Polyglot L0-L6](../01_architecture/adr/0001-polyglot-architecture.md) | L0 | ACTIVE |
| DE-V2-ADR-002 | [Ambiguity Res.](../01_architecture/adr/0002-ambiguity-resolutions.md) | L0 | ACTIVE |
| DE-V2-ADR-003 | [Agentic SFE](../01_architecture/adr/0003-agentic-communication-fabrication.md) | L2 | ACTIVE |
| DE-V2-ADR-004 | [Identity & Mood](../01_architecture/adr/0004-project-personality.md) | L0 | ACTIVE |
| DE-V2-ADR-005 | [Cognitive Standards](../01_architecture/adr/0005-cognitive-fabrication-protocols.md) | L0 | ACTIVE |
| DE-V2-ADR-010 | [L2 Memory Bridge](../01_architecture/adr/0010-l2-infrastructure-bridge.md) | L0 | ACTIVE |

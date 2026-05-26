---
status: ACTIVE
layer: meta
domain:
- core-spec
- index
- ssot
dependencies:
- specs/201_canonical_spec_binding_registry.md
- specs/202_runtime_lifecycle_chat_contract.md
- specs/L0_Overseer/00_topology_tracker.md
- specs/L0_Overseer/11_monorepo_structure.md
- specs/L0_Overseer/26_langgraph_quantum_swarm.md
- specs/L0_Overseer/28_shadow_worktrees.md
- specs/L0_Overseer/29_skill_ingestion_engine.md
- specs/L0_Overseer/43_documentation_and_artifact_standards.md
- specs/L0_Overseer/50_daemon_telemetry_contracts.md
- specs/L0_Overseer/51_model_contracts_alignment.md
- specs/L1_Nervous/10_protobuf_contracts.md
- specs/L1_Nervous/15_mcp_sidecar_isolation.md
- specs/L1_Nervous/16_mcp_dynamic_gateway.md
- specs/L1_Nervous/23_atomic_modular_nodes.md
- specs/L1_Nervous/41_layer_handshake_protocol.md
- specs/L1_Nervous/44_local_reasoning_gateway.md
- specs/L1_Nervous/49_typed_sdk_generation.md
- specs/L2_Brain/12_6d_context_model.md
- specs/L2_Brain/21_software_fabrication_engine.md
- specs/L2_Brain/27_floating_session_state.md
- specs/L2_Brain/40_token_optimization_protocol.md
- specs/L2_Brain/41_wordline_sovereignty.md
- specs/L2_Brain/42_metacognitive_identity.md
- specs/L2_Brain/81_phase_ledger.md
- specs/L2_Brain/82_long_running_mission_runtime.md
- specs/L3_Shield/22_sdd_executable_contracts.md
---

# CORE_SPEC

## Propósito
Índice maestro de documentación técnica activa del proyecto.

## Política de verdad
- Este archivo solo indexa contratos; no duplica implementación.
- Todas las rutas listadas deben existir físicamente.
- Estados permitidos: `ACTIVE`, `DRAFT`, `PROPOSED`, `DEPRECATED`.

## Documentos base
- `README.md`
- `doc/PHYSICAL_MAP.md`
- `doc/specs/43_documentation_and_artifact_standards.md`
- `doc/guides/mcp_server_usage.md`

## Especificaciones core (ACTIVE/DRAFT)
- `doc/specs/00_topology_tracker.md`
- `doc/specs/10_protobuf_contracts.md`
- `doc/specs/11_monorepo_structure.md`
- `doc/specs/12_6d_context_model.md`
- `doc/specs/15_mcp_sidecar_isolation.md`
- `doc/specs/16_mcp_dynamic_gateway.md`
- `doc/specs/21_software_fabrication_engine.md`
- `doc/specs/22_sdd_executable_contracts.md`
- `doc/specs/23_atomic_modular_nodes.md`
- `doc/specs/26_langgraph_quantum_swarm.md`
- `doc/specs/29_skill_ingestion_engine.md`
- `doc/specs/41_layer_handshake_protocol.md`
- `doc/specs/43_documentation_and_artifact_standards.md`
- `doc/specs/44_local_reasoning_gateway.md`
- `doc/specs/49_typed_sdk_generation.md`
- `doc/specs/50_daemon_telemetry_contracts.md`
- `doc/specs/51_model_contracts_alignment.md`
- `doc/specs/81_phase_ledger.md`
- `doc/specs/82_long_running_mission_runtime.md`
- `doc/specs/201_canonical_spec_binding_registry.md`
- `doc/specs/202_runtime_lifecycle_chat_contract.md`

## Especificaciones roadmap (PROPOSED)
- `doc/specs/27_floating_session_state.md`
- `doc/specs/28_shadow_worktrees.md`
- `doc/specs/40_token_optimization_protocol.md`
- `doc/specs/41_wordline_sovereignty.md`
- `doc/specs/42_metacognitive_identity.md`

## Método agéntico
- `doc/agentic/SYSTEM_PROMPT_BASE.md`
- `doc/agentic/SWARM_WORKFLOW.md`
- `doc/agentic/EXECUTION_PROTOCOL.md`
- `doc/agentic/AGENT_TASK_CONTRACT.md`
- `doc/agentic/HANDOFF_CONTRACT.md`
- `doc/agentic/VALIDATION_EVIDENCE.md`
- `doc/agentic/SCOPE_GUARD_PROTOCOL.md`
- `doc/agentic/AGENT_RELIABILITY_LEDGER.md`

## Plantillas operativas
- `.aiwg/templates/agent_task_contract.yaml`
- `.aiwg/templates/agent_handoff.md`
- `.aiwg/templates/validation_evidence.md`

## Criterio de mantenimiento
Si cambia una spec (estado, nombre o ubicación), este índice se actualiza en el mismo lote.
Antes de cerrar el lote documental, ejecutar:

```bash
python3 scripts/validate_specs_docs.py
```

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
- `doc/specs/41_layer_handshake_protocol.md`
- `doc/specs/43_documentation_and_artifact_standards.md`

## Especificaciones roadmap (PROPOSED)
- `doc/specs/26_langgraph_quantum_swarm.md`
- `doc/specs/27_floating_session_state.md`
- `doc/specs/28_shadow_worktrees.md`
- `doc/specs/29_skill_ingestion_engine.md`
- `doc/specs/40_token_optimization_protocol.md`
- `doc/specs/41_wordline_sovereignty.md`
- `doc/specs/42_metacognitive_identity.md`

## Método agéntico
- `doc/agentic/SYSTEM_PROMPT_BASE.md`
- `doc/agentic/SWARM_WORKFLOW.md`
- `doc/agentic/EXECUTION_PROTOCOL.md`

## Criterio de mantenimiento
Si cambia una spec (estado, nombre o ubicación), este índice se actualiza en el mismo lote.
Antes de cerrar el lote documental, ejecutar:

```bash
python3 scripts/validate_specs_docs.py
```

# Structural Contract Bindings

## Summary
- Total Bindings: 38
- BOUND_ACTIVE_RUNTIME: 31
- CONTRACT_BOUND: 2
- TOOLCHAIN_MISSING: 1
- TOOLCHAIN_VALIDATED: 4

## Bindings List

| Path | Layer | Status (declared->resolved) | Risk (declared->effective) | Spec Hits | Test Hits | Issues |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `layers/l0_overseer/lib/overseer/application.ex` | L0 | DEFERRED_NO_SAFE_ACTION->CONTRACT_BOUND | HIGH->MEDIUM | 3 | 0 | none |
| `layers/l0_overseer/supervisor.py` | L0 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 3 | 1 | none |
| `layers/l1_nervous/application/use_cases.py` | L1 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 4 | 1 | none |
| `layers/l1_nervous/bootstrap.py` | L1 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 4 | 1 | none |
| `layers/l1_nervous/domain/services.py` | L1 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 4 | 1 | none |
| `layers/l1_nervous/internal/skill/blueprint.go` | L1 | DEFERRED_NO_SAFE_ACTION->TOOLCHAIN_VALIDATED | HIGH->MEDIUM | 3 | 0 | none |
| `layers/l1_nervous/internal/skill/mcp_client.go` | L1 | DEFERRED_NO_SAFE_ACTION->TOOLCHAIN_VALIDATED | HIGH->MEDIUM | 3 | 0 | none |
| `layers/l1_nervous/internal/skill/types.go` | L1 | DEFERRED_NO_SAFE_ACTION->TOOLCHAIN_VALIDATED | HIGH->MEDIUM | 3 | 0 | none |
| `layers/l1_nervous/knowledge_adapters.py` | L1 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 4 | 2 | none |
| `layers/l1_nervous/mcp_registry.py` | L1 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 4 | 1 | none |
| `layers/l1_nervous/mcp_transport.py` | L1 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 4 | 1 | none |
| `layers/l1_nervous/repo_guard.py` | L1 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 4 | 1 | none |
| `layers/l1_nervous/runtime_paths.py` | L1 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 5 | 2 | none |
| `layers/l1_nervous/sidecar.go` | L1 | DEFERRED_NO_SAFE_ACTION->TOOLCHAIN_VALIDATED | HIGH->MEDIUM | 3 | 0 | none |
| `layers/l1_nervous/ssh_sandbox_wrapper.sh` | L1 | DEFERRED_NO_SAFE_ACTION->TOOLCHAIN_MISSING | HIGH->HIGH | 3 | 0 | toolchain_missing:shellcheck |
| `layers/l1_nervous/tools_impl/nervous.py` | L1 | DEFERRED_NO_SAFE_ACTION->CONTRACT_BOUND | HIGH->MEDIUM | 2 | 1 | none |
| `layers/l1_nervous/tools_impl/patch_transactions.py` | L1 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 4 | 1 | none |
| `layers/l1_nervous/utils.py` | L1 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 4 | 1 | none |
| `layers/l2_brain/action_graph.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/application/cognitive/use_cases.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/ast_indexer.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/auditor_port.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/branch_memory.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/cognition/pattern_miner_v2.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/context_circulation_runtime.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 2 | 1 | none |
| `layers/l2_brain/cypher_codec.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/domain/dtos.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/domain/hypothesis_service.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/domain/reasoning_logic.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/domain/retrieval_service.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 2 | 1 | none |
| `layers/l2_brain/domain/semantic_ports.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 2 | 1 | none |
| `layers/l2_brain/embedding_provider.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 2 | 1 | none |
| `layers/l2_brain/entity_voice.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/event_bus.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/evolution_feedback_loop.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/expansion_policy.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/formal_bridge.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |
| `layers/l2_brain/gateway_contract.py` | L2 | BOUND_ACTIVE_RUNTIME->BOUND_ACTIVE_RUNTIME | MEDIUM->MEDIUM | 1 | 1 | none |

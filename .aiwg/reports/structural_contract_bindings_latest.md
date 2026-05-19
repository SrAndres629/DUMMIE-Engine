# Structural Contract Bindings

## Summary
- Total Bindings: 18
- BOUND_ACTIVE_RUNTIME: 11
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

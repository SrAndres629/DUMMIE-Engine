# Structural Contract Bindings

## Summary
- Total Bindings: 18

## Bindings List

| Path | Layer | Owner Domain | Status | Spec Refs | Test Refs | Risk After | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `layers/l0_overseer/lib/overseer/application.ex` | L0 | Elixir App Supervisor | **DEFERRED_NO_SAFE_ACTION** | doc/specs/103_cognitive_orchestrator.md | None | `HIGH` | Elixir app supervisor specification of the overseer gateway. OTP tree compilation deferred. |
| `layers/l0_overseer/supervisor.py` | L0 | Daemon Process Supervision | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l0_overseer/tests/test_l0_contract_imports.py | `LOW` | System supervisor managing daemon restarts, locking, and sockets. |
| `layers/l1_nervous/application/use_cases.py` | L1 | Nervous Application Orchestration | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Active usecases of the L1 nervous layer orchestrating daemon processes. |
| `layers/l1_nervous/bootstrap.py` | L1 | Nervous System Integration | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Nervous system bootstrap initialization routine. Wired directly to cognitive orchestration. |
| `layers/l1_nervous/domain/services.py` | L1 | Nervous Domain Logic | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Domain services layer containing active cognitive state schemas. |
| `layers/l1_nervous/internal/skill/blueprint.go` | L1 | Go Skill Bindings | **DEFERRED_NO_SAFE_ACTION** | doc/specs/103_cognitive_orchestrator.md | None | `HIGH` | Go binary definitions of dynamic skill. Toolchain compilation deferred until next phase. |
| `layers/l1_nervous/internal/skill/mcp_client.go` | L1 | Go MCP Gateway | **DEFERRED_NO_SAFE_ACTION** | doc/specs/103_cognitive_orchestrator.md | None | `HIGH` | Fast Go JSON-RPC implementation for local sidecar daemon. Deferred due to toolchain compilation limits. |
| `layers/l1_nervous/internal/skill/types.go` | L1 | Go Types Specs | **DEFERRED_NO_SAFE_ACTION** | doc/specs/103_cognitive_orchestrator.md | None | `HIGH` | Standard definitions of memory nodes used inside the Go gateway client. |
| `layers/l1_nervous/knowledge_adapters.py` | L1 | Knowledge Integration | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Adapters bridging L1 external inputs with L2 cognitive vector representations. |
| `layers/l1_nervous/mcp_registry.py` | L1 | MCP Discovery | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Local registry managing capabilities and MCP schema binding contracts. |
| `layers/l1_nervous/mcp_transport.py` | L1 | MCP Client transport | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Asynchronous MCP client json-rpc sockets transport layer. |
| `layers/l1_nervous/repo_guard.py` | L1 | Repository Governance | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md, AGENTS.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Repository governance monitor enforcing commit hooks and rules. |
| `layers/l1_nervous/runtime_paths.py` | L1 | System Portability | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Dynamic configuration paths resolver to guarantee host OS portability. |
| `layers/l1_nervous/sidecar.go` | L1 | Go Process Sidecar | **DEFERRED_NO_SAFE_ACTION** | doc/specs/103_cognitive_orchestrator.md | None | `HIGH` | Daemon sidecar orchestrator written in Go to communicate with L0-Overseer. |
| `layers/l1_nervous/ssh_sandbox_wrapper.sh` | L1 | Sandbox Execution Shell | **DEFERRED_NO_SAFE_ACTION** | doc/specs/103_cognitive_orchestrator.md | None | `HIGH` | Executable bash sandbox harness to execute ssh routines securely. Left deferred for security auditing. |
| `layers/l1_nervous/tools_impl/nervous.py` | L1 | Nervous Skill Tools | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Skill tool executions matching L1 capabilities contracts. |
| `layers/l1_nervous/tools_impl/patch_transactions.py` | L1 | Dynamic Patching Transactions | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Atomic database and memory patch transactional isolation boundaries. |
| `layers/l1_nervous/utils.py` | L1 | Nervous Helpers | **BOUND_ACTIVE_RUNTIME** | doc/specs/103_cognitive_orchestrator.md | layers/l1_nervous/tests/test_l1_contract_imports.py | `LOW` | Generic helper functions for binary stream processing. |

# Structural Polyglot Toolchain Ledger

This ledger documents toolchain evidence and risk calibration for deferred L0/L1 target files.

| Path | Language | Required Toolchain | Status | Binding Decision | Risk After | Next Action | Done Criteria |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `layers/l0_overseer/lib/overseer/application.ex` | Elixir | `/usr/bin/mix` | DEFERRED_NO_SAFE_ACTION | `CONTRACT_BOUND` | **MEDIUM** | None, fully verified OTP substate | OTP supervisor passes compilation and tests |
| `layers/l1_nervous/internal/skill/blueprint.go` | Go | `/home/jorand/.local/bin/go` | DEFERRED_NO_SAFE_ACTION | `TOOLCHAIN_VALIDATED` | **MEDIUM** | Integrate Go unit testing for skill registry | Compiles correctly with active compiler |
| `layers/l1_nervous/internal/skill/mcp_client.go` | Go | `/home/jorand/.local/bin/go` | DEFERRED_NO_SAFE_ACTION | `TOOLCHAIN_VALIDATED` | **MEDIUM** | Integrate Go unit testing for skill registry | Compiles correctly with active compiler |
| `layers/l1_nervous/internal/skill/types.go` | Go | `/home/jorand/.local/bin/go` | DEFERRED_NO_SAFE_ACTION | `TOOLCHAIN_VALIDATED` | **MEDIUM** | Integrate Go unit testing for skill registry | Compiles correctly with active compiler |
| `layers/l1_nervous/sidecar.go` | Go | `/home/jorand/.local/bin/go` | DEFERRED_NO_SAFE_ACTION | `TOOLCHAIN_VALIDATED` | **MEDIUM** | Integrate sidecar binary integration tests | Compiles correctly alongside main.go entrypoint |
| `layers/l1_nervous/ssh_sandbox_wrapper.sh` | Shell | `/usr/bin/shellcheck` | DEFERRED_NO_SAFE_ACTION | `TOOLCHAIN_VALIDATED` | **MEDIUM** | Maintain shellcheck coverage in future CI gates | No syntax or lint errors detected by the selected shell toolchain |
| `layers/l1_nervous/tools_impl/nervous.py` | Python | `/usr/bin/python3` | DEFERRED_NO_SAFE_ACTION | `CONTRACT_BOUND` | **MEDIUM** | Reinforce unit testing for FastMCP tools | Import contract and public function signatures validated |

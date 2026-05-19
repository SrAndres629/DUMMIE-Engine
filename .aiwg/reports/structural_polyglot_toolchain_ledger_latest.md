# Structural Polyglot Toolchain Ledger — Pack 2.2

## Toolchain Detection
- go: /home/jorand/.local/bin/go
- mix: /usr/bin/mix
- elixir: /usr/bin/elixir
- shellcheck: MISSING
- bash: /usr/bin/bash
- python3: /usr/bin/python3

## Deferred Targets
| Path | Language | Decision | Risk After | Evidence Command | Observed Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `layers/l0_overseer/lib/overseer/application.ex` | Elixir | CONTRACT_BOUND | MEDIUM | `cd layers/l0_overseer && mix test` | mix test passed (1 test, 0 failures) [see elixir_probe_pack_2_2_latest.log] |
| `layers/l1_nervous/internal/skill/blueprint.go` | Go | TOOLCHAIN_VALIDATED | MEDIUM | `cd layers/l1_nervous && go test ./internal/skill/...` | internal/skill probe passed (no test files, package compiled); root-level go test still fails due proto/main conflicts [see go_probe_pack_2_2_latest.log + go_internal_skill_probe_pack_2_2_latest.log] |
| `layers/l1_nervous/internal/skill/mcp_client.go` | Go | TOOLCHAIN_VALIDATED | MEDIUM | `cd layers/l1_nervous && go test ./internal/skill/...` | internal/skill probe passed (no test files, package compiled); root-level go test still fails due proto/main conflicts [see go_probe_pack_2_2_latest.log + go_internal_skill_probe_pack_2_2_latest.log] |
| `layers/l1_nervous/internal/skill/types.go` | Go | TOOLCHAIN_VALIDATED | MEDIUM | `cd layers/l1_nervous && go test ./internal/skill/...` | internal/skill probe passed (no test files, package compiled); root-level go test still fails due proto/main conflicts [see go_probe_pack_2_2_latest.log + go_internal_skill_probe_pack_2_2_latest.log] |
| `layers/l1_nervous/sidecar.go` | Go | TOOLCHAIN_VALIDATED | MEDIUM | `cd layers/l1_nervous && go build main.go sidecar.go` | sidecar build succeeded [see go_sidecar_probe_pack_2_2_latest.log]; root module go test still fails and remains tracked. |
| `layers/l1_nervous/ssh_sandbox_wrapper.sh` | Shell | TOOLCHAIN_MISSING | HIGH | `bash -n layers/l1_nervous/ssh_sandbox_wrapper.sh` | shellcheck missing; fallback bash -n passed [see shell_probe_pack_2_2_latest.log]. |
| `layers/l1_nervous/tools_impl/nervous.py` | Python | CONTRACT_BOUND | MEDIUM | `layers/l2_brain/.venv/bin/pytest -q layers/l1_nervous/tests/test_l1_contract_imports.py -k "register_nervous_tools_signature or nervous_tools_contract_shape_without_import or tools_impl.nervous"` | Python contract probe passed (3 passed, 10 deselected) [see python_probe_pack_2_2_latest.log]. |

## Notes
- Root Go probe failed at module scope and remains explicit debt (not hidden).
- shellcheck is missing; ssh wrapper remains HIGH until shellcheck evidence exists.
- repo health is expected to remain FAIL in this phase.

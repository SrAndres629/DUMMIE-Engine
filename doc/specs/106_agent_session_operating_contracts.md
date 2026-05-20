---
spec_id: "DE-V2-L2-106"
title: "Agent Session Operating Contracts"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 106 - Agent Session Operating Contracts

## Purpose

Gemini CLI, Codex CLI, and Antigravity IDE must obey the same canonical session operating model.

## Current State

Implemented as Phase 1 session contracts under `.aiwg/session_contracts/`. The contracts define shared startup, evidence, safety, and roadmap-loading behavior for local agents.

## Physical Evidence

- `.aiwg/session_contracts/UNIVERSAL_AGENT_SESSION_CONTRACT.md`
- `.aiwg/session_contracts/ANTIGRAVITY_SESSION_CONTRACT.md`
- `.aiwg/session_contracts/CODEX_CLI_SESSION_CONTRACT.md`
- `.aiwg/session_contracts/ANTIGRAVITY_IDE_SESSION_CONTRACT.md`
- `.aiwg/context_transform/per_message_operating_contract.yaml`
- `.aiwg/evolution/current_position.json`
- `.aiwg/evolution/next_phase_seed.json`

## Requirements

- Universal session contract exists at `.aiwg/session_contracts/UNIVERSAL_AGENT_SESSION_CONTRACT.md`.
- Antigravity CLI session contract exists at `.aiwg/session_contracts/ANTIGRAVITY_SESSION_CONTRACT.md`.
- Codex CLI session contract exists at `.aiwg/session_contracts/CODEX_CLI_SESSION_CONTRACT.md`.
- Antigravity IDE session contract exists at `.aiwg/session_contracts/ANTIGRAVITY_IDE_SESSION_CONTRACT.md`.
- Every session must load `current_position.json` and `next_phase_seed.json`.
- Every session must avoid roadmap drift.
- Every session must avoid storing secrets and private chain-of-thought.

## Contract Invariants

- Every local agent session loads canonical current position and next phase seed.
- Every local agent session checks forbidden skips.
- Antigravity CLI, Codex CLI, and Antigravity IDE share the same roadmap source.
- Agent sessions must not redefine the roadmap from chat memory.
- PASS claims require evidence or documented absence.

## Verification

```bash
python3 scripts/validate_specs_docs.py --check doc/specs/106_agent_session_operating_contracts.md
python3 - <<'PY'
from pathlib import Path
contracts = [
    '.aiwg/session_contracts/UNIVERSAL_AGENT_SESSION_CONTRACT.md',
    '.aiwg/session_contracts/ANTIGRAVITY_SESSION_CONTRACT.md',
    '.aiwg/session_contracts/CODEX_CLI_SESSION_CONTRACT.md',
    '.aiwg/session_contracts/ANTIGRAVITY_IDE_SESSION_CONTRACT.md',
]
for contract in contracts:
    assert Path(contract).exists(), contract
PY
```

## Traceability

| Invariant | Evidence | Verification |
| --- | --- | --- |
| Universal contract | `.aiwg/session_contracts/UNIVERSAL_AGENT_SESSION_CONTRACT.md` | File exists |
| Antigravity contract | `.aiwg/session_contracts/ANTIGRAVITY_SESSION_CONTRACT.md` | File exists |
| Codex contract | `.aiwg/session_contracts/CODEX_CLI_SESSION_CONTRACT.md` | File exists |
| Antigravity contract | `.aiwg/session_contracts/ANTIGRAVITY_IDE_SESSION_CONTRACT.md` | File exists |
| Canonical state | `.aiwg/evolution/current_position.json` | Cold-read validation |

## Acceptance

Session contracts are accepted when a cold-read agent can locate them and determine P2 from canonical files without chat memory.

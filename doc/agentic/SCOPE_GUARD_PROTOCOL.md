---
status: ACTIVE
layer: agentic
domain: [scope, guard, protocol, safety]
---
# SCOPE_GUARD_PROTOCOL

## Purpose
Detect over-editing, drift, and unauthorized changes during agentic work.

The scope guard compares the original Agent Task Contract against the physical
diff, commands run, evidence, and handoff.

This protocol complements:
- `doc/agentic/AGENT_TASK_CONTRACT.md`
- `doc/agentic/HANDOFF_CONTRACT.md`
- `doc/agentic/VALIDATION_EVIDENCE.md`
- `doc/agentic/AGENT_RELIABILITY_LEDGER.md`

## Guard Inputs
The Validator or Integrator needs:
- the original task contract.
- `git status --short`.
- the final diff or list of changed files.
- command evidence from the agent.
- the agent handoff.

## Drift Signals

| Signal | Detection Rule | Default Severity |
| --- | --- | --- |
| Files outside scope | Changed file not matched by `allowed_files`. | BLOCK |
| Forbidden file touched | Changed file matches `forbidden_files`. | BLOCK |
| Generated file changed | Generated artifact changed without explicit permission. | BLOCK |
| Runtime touched without authority | `layers/**`, daemon, orchestrator, or persistent store touched without `RUNTIME_PATCH` or higher. | BLOCK |
| Architecture changed without docs | Runtime or contract change without matching doc update. | WARN or BLOCK |
| Docs changed without evidence | Docs claim physical truth without command or source-read evidence. | WARN |
| Claims without commands | Handoff says "passed", "fixed", or "verified" without exact command. | BLOCK |
| Root clutter added | New root-level file outside allowed scope. | WARN or BLOCK |
| Unrelated change mixed in | Diff includes changes not required by objective. | BLOCK |
| Max file count exceeded | Changed file count exceeds `max_files_changed`. | BLOCK unless preapproved. |
| Max line count exceeded | Changed line count exceeds `max_lines_changed`. | WARN or BLOCK based on risk. |

## Mandatory Pre-Edit Checks
At minimum:

```bash
git status --short
git branch --show-current
```

For 4D-TES or memory-engine work, also run the workspace-required search:

```bash
rg -n "kuzu_data|MemoryState|m\\.\\*|rm -f.*kuzu|os\\.remove\\(" layers scripts doc -S
```

## Mandatory Post-Edit Checks
At minimum:

```bash
git status --short
python3 scripts/validate_specs_docs.py
```

If validation fails, classify the failure:
- `PREEXISTING_FAILURE`: same failure is documented or reproduced before the change.
- `NEW_FAILURE`: failure appears because of the change.
- `UNKNOWN_FAILURE`: origin is not proven.

## Scope Verdicts

| Verdict | Meaning |
| --- | --- |
| `PASS` | Diff matches scope, validation evidence is present, no blocking drift. |
| `PASS_WITH_PREEXISTING_FAILURE` | Scope is clean, but an unrelated known failure remains. |
| `WARN` | Non-blocking issue exists; Integrator must record risk. |
| `BLOCK` | Work cannot close until the issue is fixed or the task contract is amended. |

## Manual Validator Checklist

1. Compare changed files to `allowed_files`.
2. Compare changed files to `forbidden_files`.
3. Confirm no generated artifacts changed unless allowed.
4. Confirm no runtime, daemon, orchestrator, or persistent data files changed unless authorized.
5. Confirm every acceptance criterion has evidence.
6. Confirm every validation command was run or explicitly blocked.
7. Confirm the handoff lists assumptions, risks, and deviations.
8. Confirm the final diff contains no unrelated cleanup.

## Example Scope Review

```yaml
task_id: phase1-agentic-contracts-builder
changed_files:
  - doc/agentic/AGENT_TASK_CONTRACT.md
  - doc/agentic/HANDOFF_CONTRACT.md
  - doc/agentic/VALIDATION_EVIDENCE.md
  - doc/agentic/SCOPE_GUARD_PROTOCOL.md
  - doc/agentic/AGENT_RELIABILITY_LEDGER.md
  - .aiwg/templates/agent_task_contract.yaml
  - .aiwg/templates/agent_handoff.md
  - .aiwg/templates/validation_evidence.md
scope_verdict: PASS_WITH_PREEXISTING_FAILURE
evidence:
  - "git status --short listed only allowed files."
  - "python3 scripts/validate_specs_docs.py failed on a documented preexisting issue outside the task scope."
deviations: []
```

## Future Automation Contract
Future checker scripts should implement this protocol without changing runtime:
- a scope guard checker.
- a handoff checker.
- an agent delivery scorer.

These scripts should read a task contract, a handoff, and current git state, then
return a machine-readable verdict.

---
status: ACTIVE
layer: agentic
domain: [handoff, contract, protocol]
---
# HANDOFF_CONTRACT

## Purpose
Define the required handoff format when one agent finishes work that another
agent, validator, or human must inspect or continue.

A handoff is not a status update. It is a transfer of responsibility backed by
files changed, commands run, validation results, evidence, assumptions, and
remaining risks.

This contract complements:
- `doc/agentic/EXECUTION_PROTOCOL.md`
- `doc/agentic/SWARM_WORKFLOW.md`
- `doc/agentic/AGENT_TASK_CONTRACT.md`
- `doc/agentic/VALIDATION_EVIDENCE.md`

## Required Handoff Structure

Every handoff must use this structure:

```markdown
# Agent Handoff

## Task ID
## Agent Role
## Objective
## Files Changed
## Commands Run
## Validation Results
## Evidence
## Assumptions
## Risks Remaining
## Scope Deviations
## Follow-up Recommendation
## Human Review Needed
```

## Field Rules

| Section | Required Content |
| --- | --- |
| `Task ID` | Must match the `task_id` from the task contract. |
| `Agent Role` | Must match the assigned role or explain the role change. |
| `Objective` | Restate the assigned objective, not a new one. |
| `Files Changed` | List every changed file. Use `None` for read-only tasks. |
| `Commands Run` | Include exact commands and exit/result summary. |
| `Validation Results` | Classify each command as pass, fail, skipped, or blocked. |
| `Evidence` | Use categories from `VALIDATION_EVIDENCE.md`. |
| `Assumptions` | List unverified claims that influenced the work. |
| `Risks Remaining` | List unresolved technical, process, or validation risks. |
| `Scope Deviations` | State `None` or explain each deviation and why it happened. |
| `Follow-up Recommendation` | One exact next task for another agent or human. |
| `Human Review Needed` | `yes` or `no`, with reason. |

## Validation Requirements

A handoff is valid only if:
- every changed file is inside `allowed_files`, or deviations are explicit.
- every required validation command is present or marked blocked.
- claims are tagged as verified, assumed, unknown, or contradictory.
- risks are listed even when the task appears successful.
- follow-up action is concrete enough for a new task contract.

## Rejection Conditions

Reject or return the handoff for correction when:
- changed files are omitted.
- commands are summarized without exact command names.
- success is claimed without command or source evidence.
- failures are hidden behind vague wording.
- scope deviations are not disclosed.
- assumptions are presented as facts.
- the handoff introduces unrelated future work as completed work.

## Minimal Example

```markdown
# Agent Handoff

## Task ID
phase1-agentic-contracts-builder

## Agent Role
Builder

## Objective
Create the Phase 1 agentic governance contracts and templates without runtime edits.

## Files Changed
- doc/agentic/AGENT_TASK_CONTRACT.md
- doc/agentic/HANDOFF_CONTRACT.md
- doc/agentic/VALIDATION_EVIDENCE.md
- doc/agentic/SCOPE_GUARD_PROTOCOL.md
- doc/agentic/AGENT_RELIABILITY_LEDGER.md
- .aiwg/templates/agent_task_contract.yaml
- .aiwg/templates/agent_handoff.md
- .aiwg/templates/validation_evidence.md

## Commands Run
- `git status --short` - exit 0
- `python3 scripts/validate_specs_docs.py` - exit 1

## Validation Results
- `git status --short`: pass, shows only expected files.
- `python3 scripts/validate_specs_docs.py`: fail, classified as PREEXISTING_FAILURE if the same spec error existed before this task.

## Evidence
- VERIFIED_BY_SOURCE_READ: existing protocols in `doc/agentic/`.
- VERIFIED_BY_COMMAND: command outputs listed above.

## Assumptions
- Optional checker scripts should wait until docs are accepted.

## Risks Remaining
- Manual enforcement remains until checker scripts are implemented.

## Scope Deviations
None.

## Follow-up Recommendation
Create a handoff checker from this contract after Phase 1 text is validated.

## Human Review Needed
Yes. Human should approve contract wording before automation enforces it.
```

## Integrator Rule
The Integrator must compare the handoff against the original task contract before
closing the work. Any mismatch must be classified as one of:
- `ACCEPTED_WITH_REASON`
- `NEEDS_FIX`
- `OUT_OF_SCOPE`
- `BLOCKED_BY_PREEXISTING_FAILURE`

---
status: ACTIVE
layer: agentic
domain: [contract, task, protocol]
---
# AGENT_TASK_CONTRACT

## Purpose
Define the minimum task contract required before an agent edits DUMMIE Engine.
It turns a human prompt into a bounded technical mission with explicit scope,
authority, validation, evidence, and handoff expectations.

This contract complements:
- `doc/agentic/EXECUTION_PROTOCOL.md`
- `doc/agentic/SWARM_WORKFLOW.md`
- `doc/agentic/VALIDATION_EVIDENCE.md`
- `doc/agentic/SCOPE_GUARD_PROTOCOL.md`

## When To Use
Use an Agent Task Contract for any agentic task that changes files, runs
project commands, validates repo state, or hands work to another agent.

Do not start implementation until the contract answers:
1. What objective must be achieved?
2. Which files may be touched?
3. Which files and commands are forbidden?
4. What authority is required?
5. Which checks prove success?
6. What evidence must be returned?
7. What handoff is required?

## Required Contract Fields

| Field | Required Meaning |
| --- | --- |
| `task_id` | Stable identifier for tracking, handoff, and ledger entries. |
| `phase` | Program phase or initiative name. |
| `role` | Agent role: `Supervisor`, `Cartographer`, `Architect`, `Builder`, `Validator`, `Integrator`, or `Checker`. |
| `objective` | One concrete mission outcome. |
| `context` | Repo facts, prior decisions, and links the agent must honor. |
| `allowed_files` | Exact files or globs the agent may read or edit. |
| `forbidden_files` | Exact files, globs, or areas the agent must not edit. |
| `allowed_commands` | Commands the agent may run without escalation. |
| `forbidden_commands` | Commands that are disallowed for this task. |
| `authority_required` | Permission class required for the task. |
| `risk_level` | Expected risk: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`. |
| `acceptance_criteria` | Observable conditions that must be true before closure. |
| `validation_commands` | Commands that must run before claiming success. |
| `evidence_required` | Evidence records required by `VALIDATION_EVIDENCE.md`. |
| `handoff_required` | Whether a structured handoff is mandatory. |
| `rollback_notes` | How to reverse the change or why rollback is not applicable. |
| `max_files_changed` | Upper bound for edited files. |
| `max_lines_changed` | Upper bound for changed lines, or `null` with justification. |
| `assumptions` | Explicit assumptions that are not yet verified. |
| `known_risks` | Risks that remain after the task is complete. |

## Authority Model

| Authority | Agent May Do |
| --- | --- |
| `ANALYZE_PLAN` | Read, inspect, reason across repo context, and produce an execution plan with required validation. Replaces obsolete `READ_ONLY`. |
| `DOCS_ONLY` | Edit approved documentation and templates only. |
| `TESTS_ONLY` | Add or update tests without runtime edits. |
| `RUNTIME_PATCH` | Edit approved runtime files and tests. Requires stronger validation. |
| `DATA_MIGRATION` | Touch persistent data formats or stores. Requires backup and migration plan. |
| `EXTERNAL_SIDE_EFFECT` | Send data outside the machine or perform public/network side effects. Requires explicit human approval. |

Use the lowest authority that can complete the task.

## Scope Rules
The task owner must define scope with physical paths, not vague areas.

Good:
```yaml
allowed_files:
  - doc/agentic/AGENT_TASK_CONTRACT.md
  - .aiwg/templates/agent_task_contract.yaml
forbidden_files:
  - layers/**
  - .env
  - .git/**
```

Bad:
```yaml
allowed_files:
  - docs
forbidden_files:
  - runtime stuff
```

## Validation Rules
Every task must include at least one validation command. `READ_ONLY` is obsolete;
analysis-only tasks must use `ANALYZE_PLAN` and still return evidence. If validation is impossible, the agent must classify the
gap as `UNKNOWN` in the evidence report and explain the blocker.

Validation commands should be specific enough that another agent can rerun them.
Examples:

```bash
git status --short
python3 scripts/validate_specs_docs.py
rg -n "kuzu_data|MemoryState|m\\.\\*|rm -f.*kuzu|os\\.remove\\(" layers scripts doc -S
```

## Evidence Rules
For each important claim, the agent must provide one of the evidence categories
defined in `doc/agentic/VALIDATION_EVIDENCE.md`:

- `VERIFIED_BY_TEST`
- `VERIFIED_BY_COMMAND`
- `VERIFIED_BY_SOURCE_READ`
- `ASSUMPTION`
- `UNKNOWN`
- `CONTRADICTION`

Unclassified claims are not accepted as closure evidence.

## Acceptance Checklist
Before implementation, the contract is valid only if:
- `objective` is narrow enough for one agent turn or handoff.
- `allowed_files` and `forbidden_files` are explicit.
- `validation_commands` include at least `git status --short`.
- runtime and persistent data are forbidden unless explicitly required.
- `evidence_required` lists command output or source reads.
- `handoff_required` is true when another agent will continue the work.

## Example

```yaml
task_id: phase1-agentic-contracts-builder
phase: "Phase 1 - Agentic Operating Spine"
role: Builder
objective: "Create task, handoff, evidence, scope guard, and reliability contracts without runtime edits."
context:
  - "Existing protocol: doc/agentic/EXECUTION_PROTOCOL.md"
  - "Existing workflow: doc/agentic/SWARM_WORKFLOW.md"
allowed_files:
  - doc/agentic/AGENT_TASK_CONTRACT.md
  - doc/agentic/HANDOFF_CONTRACT.md
  - doc/agentic/VALIDATION_EVIDENCE.md
  - doc/agentic/SCOPE_GUARD_PROTOCOL.md
  - doc/agentic/AGENT_RELIABILITY_LEDGER.md
  - .aiwg/templates/agent_task_contract.yaml
  - .aiwg/templates/agent_handoff.md
  - .aiwg/templates/validation_evidence.md
forbidden_files:
  - layers/**
  - scripts/**
  - .env
  - .git/**
allowed_commands:
  - git status --short
  - python3 scripts/validate_specs_docs.py
forbidden_commands:
  - git reset --hard
  - git clean -fd
  - rm -rf
authority_required: DOCS_ONLY
risk_level: LOW
acceptance_criteria:
  - "All required files exist."
  - "No runtime files changed."
  - "Validation command was executed and classified."
validation_commands:
  - git status --short
  - python3 scripts/validate_specs_docs.py
evidence_required:
  - "Command output for validation commands."
  - "Source-read evidence for existing agentic protocols."
handoff_required: true
rollback_notes: "Revert the eight created files if the contract set is rejected."
max_files_changed: 8
max_lines_changed: null
assumptions:
  - "Optional scripts are deferred until the contract text is accepted."
known_risks:
  - "Contracts are manually enforced until future checker scripts exist."
```

# Phase 1 Closure Report

## What Was Built
Phase 1 built the minimum governance layer for directing imperfect agents in
DUMMIE Engine:

- `doc/agentic/AGENT_TASK_CONTRACT.md`
- `doc/agentic/HANDOFF_CONTRACT.md`
- `doc/agentic/VALIDATION_EVIDENCE.md`
- `doc/agentic/SCOPE_GUARD_PROTOCOL.md`
- `doc/agentic/AGENT_RELIABILITY_LEDGER.md`
- `.aiwg/templates/agent_task_contract.yaml`
- `.aiwg/templates/agent_handoff.md`
- `.aiwg/templates/validation_evidence.md`

The contracts were indexed in `doc/CORE_SPEC.md` after adversarial review.
No runtime, daemon, orchestrator, L0/L1/L2, generated files, or persistent data
stores were modified.

## Evidence
- Builder created the eight Phase 1 contract/template files in commit `397f687`.
- P4 Validator classified the first review as `PASS_WITH_FIXES`.
- Micro-fixes updated `doc/CORE_SPEC.md`, genericized stale validation examples,
  defined reliability-ledger storage process, and tightened template defaults.
- P4 revalidation returned `PASS`.
- YAML parsing for `.aiwg/templates/agent_task_contract.yaml` returned
  `YAML_OK True`.
- `python3 scripts/validate_specs_docs.py` still fails only on specs 75/76.

## Agentic Capabilities Added
- Human prompts can be converted into scoped task contracts.
- Agents can be assigned allowed files, forbidden files, allowed commands,
  forbidden commands, authority level, risk level, acceptance criteria, and
  validation commands.
- Handoffs now require files changed, commands run, validation results,
  evidence, assumptions, risks, scope deviations, human review, and next action.
- Evidence claims are classified as verified, assumed, unknown, or contradictory.
- Scope guard rules define how to detect over-editing, generated-file drift,
  runtime edits without authority, unsupported documentation claims, and root
  clutter.
- Reliability scoring now records scope adherence, evidence quality, validation
  quality, risk detection, regressions, unrelated changes, and future-use
  recommendation.

## Risks Reduced
- Agents have less room to claim success without command evidence.
- Validators have explicit criteria for rejecting incomplete handoffs.
- Integrators can compare task contracts, changed files, commands, and evidence.
- Future refactors can be split into bounded agent tasks instead of broad prompts.
- Agent performance can be scored from records instead of impressions.

## Risks Remaining
- Enforcement is still manual until checker scripts exist.
- `validate_specs_docs.py` remains red because:
  - `doc/specs/75_mission_workbench.md` references missing
    `.aiwg/workbench/{mission_id}/`.
  - `doc/specs/76_knowledge_vault.md` references missing `.aiwg/vault/`.
- No standalone machine-readable ledger artifact exists yet; entries are stored
  in relevant reports until a task contract authorizes a separate artifact.
- Preexisting-vs-new failure classification is not automated.
- Generated-file and root-clutter allowlists are not yet executable.

## Failed Assumptions
- The earlier duplication audit mentioned a different active docs validation
  failure, but current validation fails on specs 75/76.
- The initial Builder score of `8/8` was premature before adversarial validation.
- The first contract set did not define the ledger storage process clearly enough.

## Lessons For Future Agents
- Do not treat Builder self-score as closure evidence.
- Run adversarial P4 validation before P5 closure.
- Keep examples generic when they describe preexisting validation failures.
- If a contract creates active agentic docs, update `doc/CORE_SPEC.md` or explain
  why the docs are subordinate.
- Templates should force `UNKNOWN` or explicit replacement for risk fields rather
  than defaulting to empty confidence.
- Do not mix Phase 1 governance closure with specs 75/76 truth repair.

## Phase 2 Recommendation
Proceed to:

```text
FASE 2 - Truth Repair: Specs 75/76 + Validation Green
```

Exact next task:

```text
Use the Agent Task Contract to repair docs validation failures for
doc/specs/75_mission_workbench.md and doc/specs/76_knowledge_vault.md without
touching runtime. Determine whether the missing evidence paths should be created,
changed to existing physical paths, or downgraded with explicit status.
```

## Prompt Improvements
- Require P4 Validator before accepting Builder self-score.
- Require YAML parsing for `.aiwg/templates/agent_task_contract.yaml`.
- Require stale-example checks for known validation failures.
- Require a ledger storage/update process in the first Builder pass.
- Require P5 closure to include an Agent Reliability Ledger entry.

## Agent Reliability Ledger

```yaml
- agent_id: codex-phase1-builder
  provider: Codex
  role: Builder
  task_id: phase1-agentic-operating-spine
  success: true
  scope_adherence_score: 1
  evidence_score: 2
  validation_score: 2
  risk_detection_score: 1
  introduced_regression: false
  files_changed:
    count: 8
    files:
      - doc/agentic/AGENT_TASK_CONTRACT.md
      - doc/agentic/HANDOFF_CONTRACT.md
      - doc/agentic/VALIDATION_EVIDENCE.md
      - doc/agentic/SCOPE_GUARD_PROTOCOL.md
      - doc/agentic/AGENT_RELIABILITY_LEDGER.md
      - .aiwg/templates/agent_task_contract.yaml
      - .aiwg/templates/agent_handoff.md
      - .aiwg/templates/validation_evidence.md
  unrelated_changes:
    count: 0
    files: []
  commands_run:
    - git status --short
    - git branch --show-current
    - python3 scripts/validate_specs_docs.py
    - python3 yaml parse snippet for .aiwg/templates/agent_task_contract.yaml
  notes:
    - "Initial Builder self-score was corrected by P4 review."
    - "P4 required fixes were applied and revalidated as PASS."
    - "Specs 75/76 validation failures remain outside Phase 1 scope."
  recommended_future_use: allowed

- agent_id: explorer-phase1-validator
  provider: Codex
  role: Validator
  task_id: phase1-agentic-operating-spine-p4
  success: true
  scope_adherence_score: 1
  evidence_score: 2
  validation_score: 2
  risk_detection_score: 1
  introduced_regression: false
  files_changed:
    count: 0
    files: []
  unrelated_changes:
    count: 0
    files: []
  commands_run:
    - git status --short --untracked-files=all
    - git diff --stat
    - python3 scripts/validate_specs_docs.py
    - python3 yaml parse snippet for .aiwg/templates/agent_task_contract.yaml
    - targeted rg checks for stale spec examples
  notes:
    - "Found missing CORE_SPEC indexing, stale spec example, weak template defaults, and missing ledger storage process."
    - "Revalidated micro-fixes as PASS."
  recommended_future_use: preferred
```

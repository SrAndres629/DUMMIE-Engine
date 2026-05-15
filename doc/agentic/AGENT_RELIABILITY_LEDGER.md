# AGENT_RELIABILITY_LEDGER

## Purpose
Define how DUMMIE records agent, model, or tool performance across tasks.

The ledger is used to decide which agents are reliable for future work. It
scores scope control, evidence quality, validation behavior, risk detection, and
regression impact.

## Ledger Record Schema

```yaml
agent_id:
provider:
role:
task_id:
success:
scope_adherence_score:
evidence_score:
validation_score:
risk_detection_score:
introduced_regression:
files_changed:
unrelated_changes:
commands_run:
notes:
recommended_future_use:
```

## Field Rules

| Field | Meaning |
| --- | --- |
| `agent_id` | Stable name for the agent/model/tool configuration. |
| `provider` | Codex, Gemini, Antigravity, local model, human, or other provider. |
| `role` | Role assigned by `SWARM_WORKFLOW.md`. |
| `task_id` | Must match the Agent Task Contract and handoff. |
| `success` | `true`, `false`, or `partial`. |
| `scope_adherence_score` | Score component for staying inside allowed scope. |
| `evidence_score` | Score component for quality of validation evidence. |
| `validation_score` | Score component for running required checks. |
| `risk_detection_score` | Score component for surfacing risks and contradictions. |
| `introduced_regression` | `true`, `false`, or `unknown`. |
| `files_changed` | Count and list of changed files. |
| `unrelated_changes` | Count and list of unrelated changes. |
| `commands_run` | Exact commands used for validation or inspection. |
| `notes` | Short reviewer notes. |
| `recommended_future_use` | Suggested use: `preferred`, `allowed`, `limited`, `validator_only`, or `avoid`. |

## Base Scoring Formula

Apply these points once per task:

```text
+2 objective completed
+2 validation executed
+2 evidence sufficient
+1 scope respected
+1 risks identified
-2 unrelated changes
-3 validation absent
-4 false or unverified claim
-5 breaks contract or runtime
```

Recommended interpretation:

| Total | Rating | Future Use |
| --- | --- | --- |
| `7 to 8` | Strong | `preferred` for similar tasks. |
| `4 to 6` | Adequate | `allowed` with normal review. |
| `1 to 3` | Weak | `limited`; give narrower scope. |
| `0 or below` | Unsafe | `avoid` until behavior improves. |

## Component Scoring

Use component scores to preserve why the total changed:

```yaml
scope_adherence_score: 1
evidence_score: 2
validation_score: 2
risk_detection_score: 1
```

Negative events are recorded separately:

```yaml
unrelated_changes:
  count: 0
  files: []
introduced_regression: false
```

## Evidence Requirements
A ledger entry must cite:
- the task contract.
- the handoff.
- command evidence.
- validator or integrator verdict.

Do not score an agent on vibes, style preference, or unsupported memory.

## Example Entry

```yaml
agent_id: codex-phase1-builder
provider: Codex
role: Builder
task_id: phase1-agentic-contracts-builder
success: partial
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
  - python3 scripts/validate_specs_docs.py
notes:
  - "Docs-only scope respected."
  - "Specs validation failed on a known preexisting spec 49 issue."
recommended_future_use: allowed
```

## Ledger Maintenance Rules
- Keep entries short and evidence-backed.
- Do not store secrets, private user data, or credentials.
- Prefer task-level entries over broad personality judgments.
- Update recommendations when later evidence contradicts earlier scoring.

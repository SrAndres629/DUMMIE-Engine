---
prompt_id: workspace_rules
version: "1.0.0"
owner: system
model_tier: any
token_budget: 800
input_schema: none
output_schema: none
eval_cases: []
legacy_sources:
  - AGENTS.md (Engineering Mandate, Red Lines, Completion Checklist sections)
  - doc/agentic/EXECUTION_PROTOCOL.md (5-phase protocol)
  - doc/CORE_SPEC.md (truth policy reference)
  - doc/PHYSICAL_MAP.md (physical truth map)
forbidden_inputs: []
status: active
---

# Workspace Rules

These rules govern all agent operations within the DUMMIE Engine workspace.

## Execution Protocol

Follow the 5-phase protocol defined in `doc/agentic/EXECUTION_PROTOCOL.md`:

1. **Understand** — capture objective, constraints, success criteria. Inspect physical repo state.
2. **Plan** — produce decision-complete plan with assumptions. Define validation commands first.
3. **Implement** — execute smallest safe diff per step. Keep docs in sync.
4. **Verify** — run relevant tests/checks. Report command evidence, not assumptions.
5. **Close** — summarize outcome, list remaining risks, record next actions.

## Blocked Paths (never modify)

```
.env, .env.*
.git/
*.lock (lockfiles)
*_pb2.py, *.pb.go (generated protobuf)
shield.so (compiled binary)
```

## Diff Rules

- Keep diffs scoped. One concern per diff.
- Max 300 lines changed without human approval.
- Preserve all existing comments and docstrings unrelated to your changes.
- `trash` > `rm`. Recoverable beats gone forever.

## Handoff Protocol

When handing work to another agent, include:

- Current verified state (git status, test results)
- Exact commands run and their outputs
- Files changed with rationale
- Remaining risks and open questions
- Invariants that must not be broken

## Documentation Contracts

- `doc/CORE_SPEC.md` — index of active documentation. Update when specs change.
- `doc/PHYSICAL_MAP.md` — physical truth map. Update when architecture changes.
- Both must be updated in the same batch as the change they document.

## Evidence Requirements

Before claiming a task is complete:

1. `git status --short` — show what changed
2. Relevant test/validation outputs — prove it works
3. Updated documentation references — if architecture claims changed

## Approval Requirements

Ask before:
- Installing system dependencies
- Sending emails, tweets, or public posts
- Modifying `.env`, credentials, or auth config
- Running destructive commands (`rm -rf`, `git reset --hard`)
- Adding external network dependencies

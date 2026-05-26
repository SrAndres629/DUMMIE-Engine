---
status: ACTIVE
layer: agentic
domain: [validation, evidence, quality]
---
# VALIDATION_EVIDENCE

## Purpose
Define how agents separate verified facts, command evidence, source reads,
assumptions, unknowns, and contradictions.

This contract prevents agents from closing work with unsupported claims.

## Evidence Categories

| Category | Meaning | Acceptable Support |
| --- | --- | --- |
| `VERIFIED_BY_TEST` | A test or validation suite directly checked the claim. | Exact command, exit code, and relevant output summary. |
| `VERIFIED_BY_COMMAND` | A command directly checked repo state or environment state. | Exact command, exit code, and relevant output summary. |
| `VERIFIED_BY_SOURCE_READ` | The claim is supported by reading a source file or doc. | File path and the specific fact observed. |
| `ASSUMPTION` | The claim is plausible but not verified. | Reason it was assumed and how to verify later. |
| `UNKNOWN` | The agent could not determine the claim. | Blocker and recommended verification path. |
| `CONTRADICTION` | Evidence conflicts with another claim or source. | Both conflicting sources and the unresolved question. |

## Evidence Record Format

Every important claim should be recorded as:

```yaml
- claim: "No runtime files were modified."
  category: VERIFIED_BY_COMMAND
  source: "git status --short"
  result: "Only doc/agentic and .aiwg/templates files appeared as changes."
  limitations: "Does not prove semantic quality of the docs."
```

## Command Evidence Rules
Command evidence must include:
- exact command string.
- pass, fail, skipped, or blocked result.
- exit code when available.
- short output summary.
- classification of failures as `PREEXISTING_FAILURE`, `NEW_FAILURE`, or `UNKNOWN_FAILURE` when applicable.

Do not replace command evidence with "tests passed" unless the command and result
are present.

## Source-Read Evidence Rules
Source-read evidence must include:
- file path.
- fact observed.
- whether the fact is implemented, proposed, deprecated, or unknown.

Example:

```yaml
- claim: "DUMMIE already defines a five-step execution protocol."
  category: VERIFIED_BY_SOURCE_READ
  source: "doc/agentic/EXECUTION_PROTOCOL.md"
  result: "The protocol lists Understand, Plan, Implement, Verify, and Close."
  limitations: "The file defines process, not enforcement automation."
```

## Assumption Rules
Assumptions are allowed only when they are explicit.

Each assumption must include:
- why the agent believes it.
- what risk it creates.
- how a future agent can verify or remove it.

Example:

```yaml
- claim: "The first loop should not implement checker scripts."
  category: ASSUMPTION
  source: "Phase 1 task constraints"
  result: "User prompt says scripts are optional and should not be forced without a green baseline."
  limitations: "A human may still request scripts immediately."
```

## Contradiction Rules
When evidence conflicts, agents must not choose the convenient side silently.

Required contradiction record:

```yaml
- claim: "Docs validation failed after a docs-only change."
  category: CONTRADICTION
  source: "python3 scripts/validate_specs_docs.py and pre-task validation evidence"
  result: "The same validation failure was present before the task or is isolated to files outside the task scope."
  limitations: "Requires a clean pre-task command, prior report, or commit-isolation evidence to classify with confidence."
```

## Evidence Quality Levels

| Level | Description |
| --- | --- |
| `STRONG` | Direct test or command evidence with reproducible command. |
| `ADEQUATE` | Source-read evidence or command evidence with limited scope. |
| `WEAK` | Explicit assumption with a clear verification path. |
| `UNACCEPTABLE` | Claim has no category, no source, or hides a contradiction. |

## Closure Rule
A task can close only when all acceptance criteria are backed by `STRONG` or
`ADEQUATE` evidence, or the task explicitly closes with `UNKNOWN` blockers and
does not claim success for those blockers.

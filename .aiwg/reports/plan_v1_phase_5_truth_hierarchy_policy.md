# DUMMIE PLAN V1 — P5 Truth Hierarchy & Canonicality Policy

## Decision

PASS_WITH_WARNINGS

## Summary

P5 defines an operational truth-decision policy on top of P4 metadata to prevent context choice by recency or noise.

## Advanced Reasoning Summary

Claims:
- Vague hierarchy allows low-quality recency-driven overrides.
- P4 metadata needs a deterministic conflict algorithm.
- Mirror/chat/report defaults must be non-canonical.

Objections:
- Rank-only policies fail when high-rank artifacts are stale.
- PASS claims in reports can conflict with failed tests.
- Vault/notes can drift without freshness checks.

Decisions:
- Truth-source ranks and caveats are explicit.
- Effective-rank formula with bonuses/penalties is defined.
- Unsafe artifacts are hard-rejected.
- Tie-breakers and human-review fallback are mandatory.

Risks:
- Runtime enforcement is pending.
- Legacy doc debt remains.
- Freshness coverage is incomplete in some artifact families.

## Schema Created

- `.aiwg/schemas/truth_hierarchy.schema.json`

## Spec 108 Created

- `doc/specs/108_truth_hierarchy_canonicality_policy.md`
- `doc/specs/108_truth_hierarchy_canonicality_policy.feature`
- `doc/specs/108_truth_hierarchy_canonicality_policy.rules.json`

## Truth Sources

Policy defines ranked source classes from code+tests (100) down to rejected/unsafe artifacts (0).

## Effective Truth Rank

`effective_truth_rank = base_truth_rank + evidence_bonus - staleness_penalty - risk_penalty` with hard-zero safety conditions.

## Conflict Resolution Algorithm

Collect -> reject unsafe -> normalize metadata -> apply demotion -> apply canonicality -> apply evidence -> resolve+tiebreak -> record decision.

## Canonical Source Policy

Code+tests strongest behavioral truth; specs are canonical intent; schemas canonical shape; reports/notes/chat/mirrors non-primary by default.

## Stale Demotion

Stale/unknown-freshness artifacts are demoted and blocked from high-confidence context until refreshed.

## Mirror Policy

Obsidian/human mirrors are non-canonical by default and cannot override internal canonical sources.

## Chat Policy

Chat and agent claims are non-canonical unless promoted with evidence-backed artifacts.

## Security Rejection

Secrets, credentials, private reasoning, and chain-of-thought-bearing artifacts are rejected immediately.

## Examples / Scenarios

Spec 108 scenarios cover code-vs-spec, spec-vs-report, report PASS vs failed tests, chat claims, mirror conflicts, stale vault demotion, legacy doc confidence, tie-break rules, unsafe rejection, and unknown freshness blocking high-confidence context.

## What P6 Must Govern

- layer-language map
- runtime ownership by language
- polyglot coverage in global tasks
- language-specific probes
- anti-Python-only bias

## Known Debt

- `DEBT-SPEC-LEGACY-MCP-GUIDE`

## Remaining Risks

- Policy is contract-level until enforcement phases integrate it.
- Legacy spec reference debt can still produce low-confidence contradictions.

## Next Phase

P6 — PolyglotArchitectureRegistry

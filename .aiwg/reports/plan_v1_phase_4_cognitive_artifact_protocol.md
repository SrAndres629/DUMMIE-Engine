# DUMMIE PLAN V1 — P4 Cognitive Artifact Protocol

## Decision

PASS_WITH_WARNINGS

## Summary

P4 defines the canonical Cognitive Artifact Protocol as a contract layer from P3 findings, including lifecycle, canonicality, truth rank, token role, freshness, promotion, demotion, invalidation, and security constraints.

## Schema Created

- `.aiwg/schemas/cognitive_artifact.schema.json`

## Spec 107 Created

- `doc/specs/107_cognitive_artifact_protocol.md`
- `doc/specs/107_cognitive_artifact_protocol.feature`
- `doc/specs/107_cognitive_artifact_protocol.rules.json`

## Lifecycle States

candidate, draft, verified, active, used_in_context, evaluated, promoted, indexed, stale, superseded, archived, deprecated, rejected.

## Canonicality Classes

canonical, derived, candidate, mirror, deprecated, unknown.

## Truth Rank

Defined 0-100 precedence with code+tests at top and rejected/deprecated at bottom. Higher rank wins conflicts; stale artifacts lose rank.

## Token Roles

stable_prefix, dynamic_context, evidence, retrieval_candidate, summary_only, never_prompt, human_mirror, debug_only.

## Freshness Rules

Freshness object and invalidation linkage defined. Unknown freshness cannot drive high-confidence context.

## Promotion / Demotion Rules

Promotion path defined from candidate to indexed. Demotion path defined for stale/superseded/deprecated/rejected outcomes.

## Invalidation Rules

Triggers include source/spec/test changes, truth hierarchy conflict, security violations, secret detection, private reasoning detection, and duplicate truth.

## Security Rules

Protocol forbids storing private chain-of-thought, chain-of-thought, secrets, credentials, and `.env` assignment values in artifacts.

## P3 Matrix Alignment

Protocol aligns with P3 matrix and explicitly covers all required artifact families from P3 scope.

## What P5 Must Govern

- conflict resolution mechanics
- truth rank enforcement at decision time
- canonical source precedence in mixed evidence sets
- mirror artifact defaults as non-canonical
- stale artifact demotion and reconciliation policy

## Known Debt

- `DEBT-SPEC-LEGACY-MCP-GUIDE`

## Remaining Risks

- Runtime enforcement still pending (contract exists before heavy implementations by design).
- Legacy spec references still fail docs/spec validation outside P4 scope.

## Next Phase

P5 — Truth Hierarchy & Canonicality Policy

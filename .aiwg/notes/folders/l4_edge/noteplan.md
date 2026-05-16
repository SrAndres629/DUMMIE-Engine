# NotePlan: l4_edge

## Objective
Maintain a compact, truthful, and fresh summary for `layers/l4_edge` without replacing canonical sources.

## Coverage Constraints From P8
- Keep links aligned with `.aiwg/reports/spec_coverage_matrix.json`.
- Do not claim strong coverage when layer/language linkage is partial.

## Missing Links
- Add deeper spec-test-capability mapping where currently indirect.
- Improve language-role mapping when dependency noise is high.

## Required Future Probes
- Recompute source hash and compare against manifest baseline.
- Detect new/removed tests and spec references.
- Detect drift between world model and folder note claims.

## Stale Risk
- Notes can become stale when canonical files change without refresh.

## Suggested P10 Freshness Rules
- Mark stale when source hash changes.
- Mark stale when linked specs or tests regress.
- Emit stale report entries per folder.

## Suggested P11 ContextPackage Rules
- Include folder notes by reference, not raw folder dumps.
- Load summary_only notes first; load retrieval_candidate notes only when scoped tasks demand it.

## Suggested P13 ContextQuant Rules
- Use folder notes as compression candidates with freshness gating.
- Penalize stale notes in context budget selection.

## Done Criteria
- Source hash tracked and freshness status updated.
- Coverage and canonical links remain valid.
- No note contradicts code/tests/specs/schemas/phase state.

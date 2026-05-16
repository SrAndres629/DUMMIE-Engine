# DUMMIE PLAN V1 - P8 SpecCoverageGate

## Decision

PASS_WITH_WARNINGS

## Summary

P8 establishes the first measurable coverage gate using world-model, polyglot, truth, and artifact-governance inputs. The gate isolates inherited legacy debt and records readiness constraints for P9.

## Advanced Reasoning Summary

Claims:
- Sufficient coverage now means connected spec/feature/rules + layer/language + capability/test evidence.
- Gate quality must be measured from canonical tracked files, not chat memory.
- Debt isolation is required to avoid false regressions.

Objections:
- Heuristic linking can be imperfect.
- Coverage completeness can hide weak confidence in selected layers.
- Legacy missing-spec references can contaminate naive pass/fail readings.

Decisions:
- Build a compact coverage matrix from tracked files and world-model capabilities.
- Apply explicit thresholds for triplets, layers, languages, capabilities, and tests.
- Mark legacy guide debt as inherited warning.
- Move to P9 only with matrix constraints consumed.

Risks:
- Coverage matrix freshness drift.
- Uneven non-L2 coverage confidence.
- Remaining incomplete legacy spec families require follow-up governance.

## Coverage Matrix Created

` .aiwg/reports/spec_coverage_matrix.json`

## Spec Triplet Integrity

- Total families: `100`
- Complete triplets: `97`
- Incomplete triplets: `3`
- Invalid rules JSON: `0`

## Layer Coverage

L0-L6 all have at least partial spec refs in current matrix; confidence remains uneven per layer profile.

## Language Coverage

First-party languages are covered by at least one spec or architecture reference. Dependency-only languages remain warning-level when unlinked.

## Capability Coverage

All 12 world-model native capabilities are path-backed and have spec/test/report linkage in matrix output.

## Test Linkage

Core L2 capability test linkage is present; cross-layer linkage remains less dense and is tracked as warning-level risk.

## Known Debt Isolation

`DEBT-SPEC-LEGACY-MCP-GUIDE` is isolated as inherited (`introduced_by_p8=false`, warning until repair phase).

## Coverage Thresholds

Triplet integrity, layer coverage, language coverage, capability coverage, and test linkage thresholds are defined in matrix + Spec 111 rules.

## Gate Decision

No hard blockers. Proceed with warnings:
- inherited legacy debt
- required matrix refresh on spec/test changes
- uneven cross-layer confidence

## What P9 Must Consume

- `.aiwg/world_model/project_world_model.json`
- `.aiwg/reports/spec_coverage_matrix.json`
- `.aiwg/schemas/spec_coverage_gate.schema.json`
- `.aiwg/schemas/cognitive_artifact.schema.json`
- `.aiwg/schemas/truth_hierarchy.schema.json`

## Known Warnings

Legacy guide debt persists and incomplete legacy spec families remain in matrix.

## Remaining Risks

Coverage link inference is partially heuristic and must be revalidated when repository structure changes.

## Next Phase

P9 - FolderNotes + NotePlans

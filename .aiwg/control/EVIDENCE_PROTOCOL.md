# Evidence Protocol

## Purpose
Rank evidence so DUMMIE can distinguish supported claims, contradictions, assumptions, and insufficient evidence.

## Agent
EpistemicJudge owns claim evaluation; Validator verifies test and command evidence.

## Format
Evidence items use dictionaries with `type`, `supports`, `contradicts`, `ref`, and optional summary.

## Authority Order
- test: 1.0
- typed_schema: 0.9
- source_code: 0.85
- physical_map: 0.75
- core_spec: 0.70
- active_spec: 0.65
- generated_report: 0.45
- comment: 0.25

## Prohibited
- Treating generated reports as source of truth over code or tests.
- Declaring completion without fresh verification output.

## Validation
Use `EpistemicJudge.evaluate_claim` and attach the command or file evidence refs.

## 4D-TES / 6D Connection
Evidence refs are persisted in session events and validation artifacts.

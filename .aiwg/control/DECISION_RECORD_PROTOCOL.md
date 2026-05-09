# Decision Record Protocol

## Purpose
Capture why DUMMIE chooses a plan, patch boundary, or next loop.

## Agent
ColdPlanner writes decisions; Integrator validates final state.

## Format
Decision records include decision, evidence, confidence, rejected options, rollback, and validation.

## Allowed
- Markdown decision logs.
- JSONL event references.
- Explicit rollback notes.

## Prohibited
- Decisions without evidence.
- Expanding scope without updating constraints.

## Validation
Decision records must point to tests, specs, source code, or generated reports with authority classification.

## 4D-TES / 6D Connection
Decision records are linked to session events and Lamport order.

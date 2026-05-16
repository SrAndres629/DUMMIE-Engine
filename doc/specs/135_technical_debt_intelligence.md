# Spec 135: Technical Debt Intelligence

## Purpose
Identify integration gaps, broken specs, missing tests, and architectural drift autonomously.

## Scope
- Scans `repo_inventory` and generated dossiers.
- Cross-references with `spec_coverage_matrix` and Plan V1 reports.

## Runtime Behavior
1. Analyze missing tests for runtime modules.
2. Analyze missing runtime modules for defined specs.
3. Detect multiple sources of truth.
4. Output a `TechnicalDebtIntelligenceReport` and an `integration_backlog.json`.

## Safety Rules
- Report-only. Does not delete or rewrite files autonomously.

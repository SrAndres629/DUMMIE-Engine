# Spec 136: Plan V1 Completion Review

## Purpose
Assess the actual physical implementation of Plan V1, score capabilities, and differentiate between simulated, advisory, and fully autonomous actions.

## Scope
- Scores core Plan V1 capabilities.
- Produces a final completion review.

## Runtime Behavior
1. Read technical debt, folder/file dossiers, and earlier runtime outputs.
2. Evaluate each P1-P31 capability.
3. Generate a `CapabilityScorecard`.
4. Output the `PlanV1CompletionReviewReport`.

## Safety Rules
- Must accurately report when autonomy is gated or simulated. Do not claim unsafe autonomy is implemented.

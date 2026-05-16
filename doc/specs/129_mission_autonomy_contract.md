# Spec 129: Mission Autonomy Contract

## Purpose
Define and enforce authority boundaries for agentic actions based on risk, mission phase, and debate results.

## Scope
- Scopes: ADVISORY_ONLY, READ_ONLY_ANALYSIS, PLAN_GENERATION, TEST_COMMAND_RECOMMENDATION, PATCH_PROPOSAL_ONLY, HUMAN_APPROVED_WORKSPACE_EDIT, TRUSTED_WORKSTATION_REQUIRED.
- Denials: .env, credentials, network, external actions, unauthorized mutation.

## Runtime Behavior
1. Receive an `AutonomyRequest` with a requested scope and action.
2. Verify if the mission is blocked by Debate Review.
3. Check static denial policies (no secrets, no network).
4. Evaluate if the scope requires Human Approval (workspace mutation).
5. If phase is P28, defer workstation actions to P29.
6. Issue an `AutonomyDecision` (ALLOW|DENY|BLOCK).

## Safety Rules
- Workspace mutation ALWAYS requires `human_approval` in P28.
- Credentials and `.env` access are ALWAYS blocked.
- External/Network actions are ALWAYS denied in P28.

## Relationship to P29
This contract is the prerequisite gate for `TrustedWorkstationMode`.

---
spec_id: "129_mission_autonomy_contract"
title: "129 Mission Autonomy Contract"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_1"
last_verified_on: "2026-05-16"
---

# Spec 129: Mission Autonomy Contract

## Purpose
Define and enforce authority boundaries for agentic actions based on risk, mission phase, and debate results.

## Scope
- Active cognitive scopes: ADVISORY_ONLY, ANALYZE_PLAN, SPEC_AUTHORING, TEST_COMMAND_RECOMMENDATION, PATCH_PROPOSAL.
- Verified mutation scopes: WORKSPACE_WRITE, TEST_EXECUTION, COMMIT_PUSH.
- Obsolete scopes: READ_ONLY_ANALYSIS, PLAN_GENERATION, PATCH_PROPOSAL_ONLY, HUMAN_APPROVED_WORKSPACE_EDIT.
- Denials: .env, credentials, network, external actions, unauthorized mutation.

## Runtime Behavior
1. Receive an `AutonomyRequest` with a requested scope and action.
2. Verify if the mission is blocked by Debate Review.
3. Check static denial policies (no secrets, no network).
4. Evaluate if the scope is active, obsolete, or requires verification evidence.
5. If phase is P28, defer workstation actions to P29.
6. Issue an `AutonomyDecision` (ALLOW|ALLOW_WITH_VERIFICATION|ALLOW_WITH_HUMAN_APPROVAL|DENY|BLOCK).

## Safety Rules
- Workspace mutation can execute when the request includes verification evidence; otherwise it requires `human_approval`.
- `READ_ONLY_ANALYSIS` is obsolete and must be replaced by `ANALYZE_PLAN`.
- Credentials and `.env` access are ALWAYS blocked.
- External/Network actions are ALWAYS denied in P28.

## Relationship to P29
This contract is the prerequisite gate for `TrustedWorkstationMode`.

## Current State
- Runtime migrated from read-only analysis defaults to active cognitive scopes plus verified mutation scopes.

## Physical Evidence
- `layers/l2_brain/mission/mission_autonomy_contract.py`
- `layers/l2_brain/flat_brain/mission_autonomy_contract.py`
- `layers/l2_brain/tests/test_mission_autonomy_contract.py`

## Contract Invariants
- Obsolete read-only scopes are denied.
- Cognitive scopes can execute immediately when they do not mutate the workspace.
- Mutating scopes require verification evidence or human approval.
- Credential, `.env`, network, and external-action denials dominate all scope grants.

## Verification
- `uv run pytest -q layers/l2_brain/tests/test_mission_autonomy_contract.py`

## Traceability
- Spec 130 consumes the same active-scope model for workstation actions.

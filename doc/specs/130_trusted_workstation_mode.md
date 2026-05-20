---
spec_id: "130_trusted_workstation_mode"
title: "130 Trusted Workstation Mode"
status: "ACTIVE"
canonicality: "canonical"
artifact_type: "spec"
plan: "DUMMIE PLAN V1"
layer: "l2_brain"
created_by: "operationalization_pack_1"
last_verified_on: "2026-05-16"
---

# Spec 130: Trusted Workstation Mode

## Purpose
Provide a secure classification and evaluation gate for workstation-level actions, ensuring they are authorized by the MissionAutonomyContract and safe to propose.

## Scope
- Active cognitive categories: ANALYZE_PLAN, SPEC_AUTHORING, TEST_COMMAND_RECOMMENDATION, PATCH_PROPOSAL.
- Verified mutation categories: WORKSPACE_WRITE, WORKSPACE_EDIT, TEST_EXECUTION, TEST_RUN, COMMIT_PUSH.
- Obsolete categories: READ_ONLY_STATUS, READ_ONLY_FILE_METADATA, READ_ONLY_REPO_INSPECTION.
- Blocked categories: BROWSER_CONTROL, NETWORK_ACTION, CREDENTIAL_ACCESS, ENV_ACCESS, OS_MUTATION, INSTALL_DEPENDENCY, DANGEROUS_OPERATION.
- Gates: MissionAutonomyContract verification, sensitive path blocking (.env, .ssh).

## Runtime Behavior
1. Receive a `WorkstationAction` request.
2. Classify the action into a risk category.
3. Apply static safety policies (deny browser, network, credentials, etc.).
4. Determine if verification evidence is sufficient or `human_approval` is required.
5. Produce a `WorkstationDryRunResult`.

## Safety Rules
- `READ_ONLY_*` categories are obsolete and must be replaced by `ANALYZE_PLAN`.
- Governed execution is enabled for verified workspace mutation.
- Workspace mutation can execute when verification evidence is attached; otherwise it requires authorization.
- Dangerous operations (OS mutation, installs) are strictly blocked.
- Credentials and `.env` access are strictly blocked.

## Relationship to P28
Consumes the MissionAutonomyContract policies to authorize or deny specific local actions.

## Current State
- Runtime migrated from read-only workstation actions to active cognitive and verified mutation categories.

## Physical Evidence
- `layers/l2_brain/flat_brain/trusted_workstation_mode.py`
- `layers/l2_brain/tests/test_trusted_workstation_mode.py`

## Contract Invariants
- Obsolete read-only categories are denied.
- Cognitive categories can execute immediately when they do not mutate the workspace.
- Mutation categories can execute with verification evidence or require authorization.
- Sensitive paths and forbidden categories always block.

## Verification
- `uv run pytest -q layers/l2_brain/tests/test_trusted_workstation_mode.py`

## Traceability
- Spec 129 defines the mission-level autonomy model consumed by workstation gating.

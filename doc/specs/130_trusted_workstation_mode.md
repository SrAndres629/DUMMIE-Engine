# Spec 130: Trusted Workstation Mode

## Purpose
Provide a secure classification and evaluation gate for workstation-level actions, ensuring they are authorized by the MissionAutonomyContract and safe to propose.

## Scope
- Categories: READ_ONLY_STATUS, WORKSPACE_EDIT, TEST_RUN, COMMIT_PUSH, BROWSER_CONTROL, etc.
- Gates: MissionAutonomyContract verification, sensitive path blocking (.env, .ssh).

## Runtime Behavior
1. Receive a `WorkstationAction` request.
2. Classify the action into a risk category.
3. Apply static safety policies (deny browser, network, credentials, etc.).
4. Determine if `human_approval` is required (mutation actions).
5. Produce a `WorkstationDryRunResult`.

## Safety Rules
- **Actual execution is disabled by default** in P29.
- Dangerous operations (OS mutation, installs) are strictly blocked.
- Credentials and `.env` access are strictly blocked.

## Relationship to P28
Consumes the MissionAutonomyContract policies to authorize or deny specific local actions.

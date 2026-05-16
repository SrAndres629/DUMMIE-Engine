# Spec 121: State Coherence Guard

## Purpose
Ensure that all generated reports and control surface outputs (latest artifacts) are coherent with the canonical state defined in `.aiwg/evolution/`.

## Scope
- Canonical State: `current_position.json`, `next_phase_seed.json`.
- Tracked Artifacts: `cli_control_plane_latest.json`, `process_monitor_latest.json`, `dashboard_l6_latest.json`, `dashboard_l6_latest.html`.

## Runtime Behavior
1. Read canonical current_phase and next_phase.
2. Inspect each tracked artifact for its own current_phase and next_phase fields.
3. Compare them.
4. If they mismatch, report an ERROR finding.
5. If an artifact is missing, report a WARNING finding.
6. Produce a `StateCoherenceReport` with a final decision (PASS|PASS_WITH_WARNINGS|FAIL).

## Inputs
- `.aiwg/evolution/current_position.json`
- `.aiwg/evolution/next_phase_seed.json`
- `.aiwg/reports/*_latest.json`
- `.aiwg/reports/dashboard_l6_latest.html`

## Outputs
- `.aiwg/reports/state_coherence_guard_latest.json`

## Safety Rules
- Do not modify canonical state files.
- Read-only access to evolution files.
- Report only; do not attempt auto-repair unless requested.

---
spec_id: "176_daemon_gateway_heartbeat_bridge"
title: "Daemon/Gateway Heartbeat Bridge"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
---

## Purpose
This spec establishes the daemon/gateway heartbeat bridge (HEARTBEAT-2) to safely route decisions and actions to gateway channels without triggering uncontrolled background execution.

## Current State
Under implementation. Will compile dispatch envelopes conforming to `daemon_gateway_heartbeat_bridge.schema.json`.

## Physical Evidence
- Core module: `layers/l2_brain/daemon_gateway_heartbeat_bridge.py`
- Test suite: `layers/l2_brain/tests/test_daemon_gateway_heartbeat_bridge.py`
- JSON Schema: `.aiwg/schemas/daemon_gateway_heartbeat_bridge.schema.json`
- Output reports: `.aiwg/reports/daemon_gateway_heartbeat_bridge_latest.json` and `.aiwg/reports/daemon_gateway_heartbeat_bridge_latest.md`

## Contract Invariants
- **Approval Gate**: If an action is flagged as a mutation or code change, `requires_human_approval` must be `true` and `can_execute_now` must be `false`.
- **Target Restriction**: Dispatch targets are restricted to: `local`, `daemon_invocation`, `gateway`, `antigravity`, `codex`, `gemini`, `human_review`.
- **Observer Safeguard**: Operating mode is restricted to non-destructive configurations (`observe_only`, `advisory`, `repair_planning`, `patch_proposal`).

## Verification
Run tests via pytest:
```bash
python3 -m pytest layers/l2_brain/tests/test_daemon_gateway_heartbeat_bridge.py
```

## Traceability
- Maps to: `dummie_whole_body_integration_manifest.md` (HEARTBEAT-2)
- Contract Schema: `daemon_gateway_heartbeat_bridge.schema.json`

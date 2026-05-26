# L0 Autonomous Heartbeat

⚠️ **Status:** OPERATIONAL_WITH_WARNINGS
⚠️ **Mode:** observe_only
⚠️ **Decision:** PASS_WITH_WARNINGS
⚠️ **Last Run:** 2026-05-25 15:41:33 UTC (0h 3m ago)
⚠️ **Total Heartbeats:** 25
⚠️ **Coherence Score:** 0.0%

## Active Blockers
kuzu_degraded

## Last Cycle Summary
- **What it did:** Git state verified; Loaded 6 canonical inputs; Found 12 missing inputs; Truth hygiene scan completed; Epistemic state built
- **What it thought:** Coherence score: 0.0%; Active modules: 0; Shadow modules: 0; WARNING: whole_body_verification_audits_failed: No module named 'kuzu_graph_readback_verifier'; WARNING: Missing canonical inputs: self_improvement_action_queue.json, evolution_delta_application_latest.json, readiness_score_calibration_latest.json, whole_body_scan_latest.json, whole_body_scan_calibration_latest.json, wiring_matrix_latest.json, shadow_runtime_classification_latest.json, dependency_reproducibility_latest.json, embedding_activation_verification_latest.json, capability_promotion_governor_latest.json, full_body_operational_audit_latest.json, whole_body_repair_queue_latest.json
- **Dispatch:** local
- **Selected Action:** {'action_id': 'hb-fallback', 'action_type': 'generate_action_queue', 'priority': 'medium', 'status': 'proposed'}
- **Degraded Capabilities:** 3

## Warnings
- whole_body_verification_audits_failed: No module named 'kuzu_graph_readback_verifier'
- Missing canonical inputs: self_improvement_action_queue.json, evolution_delta_application_latest.json, readiness_score_calibration_latest.json, whole_body_scan_latest.json, whole_body_scan_calibration_latest.json, wiring_matrix_latest.json, shadow_runtime_classification_latest.json, dependency_reproducibility_latest.json, embedding_activation_verification_latest.json, capability_promotion_governor_latest.json, full_body_operational_audit_latest.json, whole_body_repair_queue_latest.json
- Systemic Coherence Score (0.0%) is under 60% — autonomous execution is strictly blocked.
- Systemic Body Score (0.0%) is under 90% — autonomous scaling and execution are strictly blocked.
- Daemon background runtime is simulated — autonomous runtime claim is blocked.
- Optional polyglot toolchains are missing: rust, cargo, elixir, mix — full operational readiness is disabled.
- No eligible actions in queue; recommending action queue regeneration

---
*Updated: 2026-05-25T11:45:14Z*

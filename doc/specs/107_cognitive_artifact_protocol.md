---
spec_id: "DE-V2-L2-107"
title: "Cognitive Artifact Protocol"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-16"
version: "1.0.0"
namespace: "dummie.engine.plan_v1"
---
# Spec 107 - Cognitive Artifact Protocol

## Purpose
Define a canonical artifact contract so DUMMIE can govern lifecycle, canonicality, truth rank, freshness, token role, ownership, and invalidation consistently.

## Scope
Applies to all artifact families audited in P3 and to future artifacts that enter cognition, governance, retrieval, reporting, or runtime decision loops.

## Current State
Implemented in P4 as a schema + spec contract baseline without introducing new runtime modules. Enforcement runtimes are intentionally deferred to later phases.

## Physical Evidence
- `.aiwg/schemas/cognitive_artifact.schema.json`
- `.aiwg/reports/plan_v1_phase_4_cognitive_artifact_protocol.md`
- `.aiwg/reports/plan_v1_phase_4_cognitive_artifact_protocol.json`
- `doc/specs/107_cognitive_artifact_protocol.md`
- `doc/specs/107_cognitive_artifact_protocol.feature`
- `doc/specs/107_cognitive_artifact_protocol.rules.json`

## Artifact Fields
Required protocol fields:
- artifact_id
- artifact_type
- artifact_version
- title
- summary
- canonicality
- truth_rank
- lifecycle_state
- owner_runtime
- source_refs
- source_hashes
- linked_specs
- linked_tests
- linked_layers
- linked_languages
- token_role
- freshness
- promotion_rules
- demotion_rules
- invalidation_rules
- runtime_consumers
- evidence_refs
- risk_flags
- created_at
- updated_at

## Lifecycle States
- candidate
- draft
- verified
- active
- used_in_context
- evaluated
- promoted
- indexed
- stale
- superseded
- archived
- deprecated
- rejected

State meaning:
- candidate: proposed but not verified.
- draft: created but not validated.
- verified: checked against evidence/tests/specs.
- active: accepted for operational use.
- used_in_context: loaded into prompt/context package.
- evaluated: outcome impact was assessed.
- promoted: upgraded to vault/world model/protocol.
- indexed: indexed for retrieval/graph/search.
- stale: source changed or freshness expired.
- superseded: replaced by newer artifact.
- archived: retained for history but not active.
- deprecated: should not be used for new reasoning.
- rejected: evaluated and rejected.

## Canonicality Classes
- canonical
- derived
- candidate
- mirror
- deprecated
- unknown

Rules:
- canonical: source of operational truth.
- derived: generated from canonical/evidence sources.
- candidate: proposed, not accepted.
- mirror: external/human-readable copy, not source of truth.
- deprecated: retained but should not govern behavior.
- unknown: classification missing; must be audited.

Default interpretations:
- Obsidian, if added later, is mirror by default, not canonical.
- Chat history is never canonical by default.
- Reports are evidence/derived unless promoted by protocol.
- Specs are canonical contracts but still require freshness/source tracking.
- Code and tests outrank stale docs.

## Truth Rank
- 100 physical source code + passing tests
- 90 active specs and rules
- 80 phase ledger / mission runtime state
- 75 daemon outcome / validation result
- 70 learning episode with evidence
- 65 vault entry with evidence
- 60 cognitive artifact marked active
- 50 report with evidence
- 40 note/folder note with freshness
- 30 human mirror / Obsidian export
- 20 chat transcript
- 10 unknown legacy doc
- 0 rejected/deprecated artifact

Rules:
- Higher truth rank wins in conflicts.
- Lower rank can provide context but cannot override higher rank.
- Stale artifacts lose rank.
- Artifacts without evidence_refs cannot be promoted above derived/candidate.

## Freshness
Freshness object:
```json
{
  "status": "fresh|stale|unknown|not_applicable",
  "last_verified": "",
  "source_hashes": {},
  "invalidation_triggers": [],
  "stale_reason": ""
}
```

Freshness rules:
- Artifacts based on source files should track source_hashes.
- If source changes, artifact becomes stale.
- If linked spec changes, artifact becomes stale.
- If linked tests fail, artifact becomes suspect.
- If freshness is unknown, artifact cannot be high-confidence context.

## Token Roles
- stable_prefix
- dynamic_context
- evidence
- retrieval_candidate
- summary_only
- never_prompt
- human_mirror
- debug_only

Role rules:
- stable_prefix: safe to place in reusable prompt prefix.
- dynamic_context: mission-specific context.
- evidence: cited support.
- retrieval_candidate: may be fetched if relevant.
- summary_only: use compressed form by default.
- never_prompt: do not include in model context.
- human_mirror: for UI/human review only.
- debug_only: use only in audits/debugging.

## Promotion Rules
- candidate -> draft: artifact is created with required metadata.
- draft -> verified: evidence_refs exist and required JSON/YAML/BDD validation passes.
- verified -> active: owner runtime or phase report accepts it.
- active -> used_in_context: referenced by context receipt or prompt frame.
- used_in_context -> evaluated: phase outcome records impact.
- evaluated -> promoted: positive reusable learning or canonical decision.
- promoted -> indexed: vault/graph/search indexing succeeds.

## Demotion Rules
- active -> stale: source hash/spec/test invalidates it.
- active -> superseded: newer accepted artifact replaces it.
- active -> deprecated: governance marks it no longer valid.
- candidate/draft -> rejected: validation fails or conflicts with higher truth.

## Invalidation Rules
Triggers:
- source_file_changed
- linked_spec_changed
- linked_test_failed
- runtime_consumer_changed
- truth_hierarchy_conflict
- manual_mentor_rejection
- security_policy_violation
- secret_detected
- private_reasoning_detected
- duplicate_truth_detected

Hard rules:
- secret_detected invalidates artifact immediately.
- private_reasoning_detected invalidates artifact immediately.
- truth_hierarchy_conflict requires reconciliation.
- duplicate_truth_detected requires merge/deprecate decision.

## Security Restrictions
Forbidden in artifacts:
- private chain-of-thought
- chain-of-thought
- secrets
- credentials
- .env assignment values

## Contract Invariants
- Artifacts must carry protocol metadata required by schema.
- Canonicality and truth rank must exist before artifact promotion.
- Freshness unknown artifacts cannot be treated as high-confidence context.
- Mirrors (including Obsidian exports) are non-canonical by default.
- Chat transcripts are non-canonical by default.
- Secret-bearing and private-reasoning-bearing artifacts are invalid immediately.

## Relationship to P3 Matrix
P4 protocol covers all required P3 artifact families:
spec_md, spec_feature, spec_rules_json, schema_json, report_md, report_json, phase_ledger, mission_state, recovery_packet, next_action, learning_episode, vault_entry, memory_ref, context_package, context_receipt, prompt_frame, prompt_cache_ledger, session_contract, evolution_roadmap, mental_model, context_transform, tool_manifest, skill_manifest, agent_manifest, mcp_manifest, registry, folder_note, noteplan, walkthrough, task, decision_record, research_brief, evidence_card, world_model, source_code_runtime, test_file, legacy_doc.

If new families are audited later, protocol applies by default until superseded.

## Relationship to P5 Truth Hierarchy
P5 must enforce conflict resolution and precedence using truth_rank + canonicality + freshness + evidence quality.

## Relationship to P9 FolderNotes + NotePlans
P9 artifacts must adopt this schema, especially token_role, freshness, and demotion/invalidation behavior.

## Relationship to P13 ContextQuantRuntime
P13 must consume token_role, truth_rank, freshness, and lifecycle_state as scoring inputs, not ad-hoc heuristics.

## Verification
```bash
python3 scripts/validate_specs_docs.py --check doc/specs/107_cognitive_artifact_protocol.md
python3 - <<'PY'
import json
from pathlib import Path

required = [
    '.aiwg/schemas/cognitive_artifact.schema.json',
    'doc/specs/107_cognitive_artifact_protocol.rules.json'
]
for p in required:
    json.loads(Path(p).read_text(encoding='utf-8'))
print('spec 107 evidence parse PASS')
PY
```

## Traceability
- Phase: `P4` Cognitive Artifact Protocol
- Previous phase input: `.aiwg/reports/artifact_lifecycle_matrix.json`
- Next phase dependency: `P5` Truth Hierarchy & Canonicality Policy

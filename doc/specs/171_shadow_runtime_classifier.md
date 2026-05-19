---
spec_id: "171_shadow_runtime_classifier"
title: "Shadow Runtime Classifier"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-17"
---

## Purpose
This specification establishes the non-destructive auditor of shadow modules (HEARTBEAT-1.1). It classifies modules identified as unwired/unmapped into logical operational roles (e.g., CLI entrypoint, dynamic import candidate, script support, test utility) to clarify their status without deleting or moving them.

## Current State
Fully implemented in the L2 Brain layer. Consumed by the metacognitive heartbeat to verify shadow module debt and output recommended actions.

## Physical Evidence
- Core module: `layers/l2_brain/flat_brain/shadow_runtime_classifier.py`
- Test suite: `layers/l2_brain/tests/test_shadow_runtime_classifier.py`
- Output report JSON: `.aiwg/reports/shadow_runtime_classification_latest.json`
- Output report Markdown: `.aiwg/reports/shadow_runtime_classification_latest.md`

## Contract Invariants
- **Non-Destructive Classification:** Must never mutate, delete, or move workspace files.
- **Classification Categories:** Must map shadow elements to known categories (`cli_entrypoint`, `script_entrypoint`, `dynamic_import_candidate`, `test_only_support`, `legacy_candidate`, `orphan_candidate`, `generated_or_build_artifact`, `documentation_support`, `needs_manual_review`, `safe_to_ignore`).
- **Recommended Actions:** Must output exact action recommendations (`wire`, `test`, `spec`, `archive`, `ignore`, `manual_review`, `do_not_touch`).

## Verification
Run tests:
```bash
python3 -m pytest layers/l2_brain/tests/test_shadow_runtime_classifier.py
```

## Traceability
- Maps to: Spec 168
- Contract Schema: `shadow_runtime_classification.schema.json`

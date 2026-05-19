---
spec_id: "169_whole_body_scan_calibrator"
title: "Whole-Body Scan Calibrator"
status: "ACTIVE"
layer: "L2"
last_verified_on: "2026-05-17"
---

## Purpose
This specification establishes the structural validation, timing audit, and reproducibility verification (HEARTBEAT-1.1) of the whole-body repository scanner. It ensures that scan metrics are accurate, stable, schema-compliant, and that the Pytest suite counts are fully reconciled.

## Current State
Fully implemented in L2 Brain layer. Automatically executed during the observe phase of the recurring metacognitive heartbeat. Emits structured calibration reports.

## Physical Evidence
- Core module: `layers/l2_brain/flat_brain/whole_body_scan_calibrator.py`
- Test suite: `layers/l2_brain/tests/test_whole_body_scan_calibrator.py`
- Output report JSON: `.aiwg/reports/whole_body_scan_calibration_latest.json`
- Output report Markdown: `.aiwg/reports/whole_body_scan_calibration_latest.md`

## Contract Invariants
- **Reproducibility Verification:** Must verify timing performance and construct reproducible hashes of scanned files.
- **Metric Verification:** Must check active modules, shadow modules, orphaned tests, stale reports, and unvalidated specifications counts.
- **Test Reconciliation:** Must reconcile total active Pytest counts to prevent model and developer misinterpretation.

## Verification
Run tests:
```bash
python3 -m pytest layers/l2_brain/tests/test_whole_body_scan_calibrator.py
```

## Traceability
- Maps to: Spec 168
- Contract Schema: `whole_body_scan_calibration.schema.json`

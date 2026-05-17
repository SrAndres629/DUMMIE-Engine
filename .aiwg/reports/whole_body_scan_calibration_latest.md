# DUMMIE Whole-Body Scan Calibration Report

**Calibration ID:** `cal-2c32acbc`
**Timestamp:** 2026-05-17T00:53:49.134245+00:00

## Calibration Decision: **PASS_WITH_WARNINGS**

### Scanner Timings and Reproducibility
- **Runtime Seconds:** `8.4631s`
- **Reproducibility Hash:** `eab2ea9848c06c5711cc801a9d41d394da2053f680520a878167dd75faf7cd66`
- **Freshness Timestamp:** 2026-05-17T00:53:46.977510+00:00

### Test Reconciliation Matrix
- **Suite Total Tests:** `46`
- **Reconciled Status:** `RECONCILED`
- **Explanation:** The repository contains 46 passing tests in the complete test suite. Executing 'test_whole_body_scanner.py' alone correctly outputs '1 passed' as it only verifies the AST whole-body scanner in isolation.

### Validated Scan Metrics
- **Active Modules Count:** 364
- **Shadow Modules Count:** 152
- **Orphaned Tests Count:** 79
- **Stale Reports Count:** 59
- **Unvalidated Specs Count:** 42

### Active Warnings
- [WARNING] Scanner runtime is high: 8.4631s (threshold: 8.0s)
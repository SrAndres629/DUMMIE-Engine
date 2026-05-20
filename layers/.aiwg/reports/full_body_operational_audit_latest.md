# Full Body Operational Audit Report
**Decision**: `PASS_WITH_WARNINGS`  
**Body Score**: `77.0%`  
**Next Recommended Repair**: `activate_local_embedding_model`

## Organ Taxonomy Summary
- **Ready Organs**: ['brain', 'nervous_system', 'mouth', 'immune_system', 'skin']
- **Degraded Organs**: ['eyes', 'memory']
- **Fallback Organs**: ['memory', 'metabolism', 'hands', 'polyglot_body']
- **Unwired Organs**: ['hands']
- **Shadow Organs**: []

## Top Body Gaps Identified
- Whole-Body Scanner not fully active or scan reports missing.
- Kùzu DB 4D-TES is READY_CANDIDATE (verified in sandbox only, lacks production readback).
- Metabolism uses static token cost estimation instead of dynamic metrics.
- Hands (Gateway live dispatch) runs in dry-run/manual-only mode.
- Polyglot Body runs in Python-only fallback. Compile/test lifecycles are unwired.

## Warnings
- System body is not fully complete (Body Score: 77.0% < 90%).

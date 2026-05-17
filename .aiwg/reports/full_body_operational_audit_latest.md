# Full Body Operational Audit Report
**Decision**: `PASS_WITH_WARNINGS`  
**Body Score**: `82.0%`  
**Next Recommended Repair**: `activate_local_embedding_model`

## Organ Taxonomy Summary
- **Ready Organs**: ['eyes', 'brain', 'nervous_system', 'mouth', 'immune_system', 'skin']
- **Degraded Organs**: ['memory']
- **Fallback Organs**: ['metabolism', 'hands', 'polyglot_body']
- **Unwired Organs**: ['hands']
- **Shadow Organs**: []

## Top Body Gaps Identified
- Memory spine or embeddings are degraded or fallback.
- Metabolism uses static token cost estimation instead of dynamic metrics.
- Hands (Gateway live dispatch) runs in dry-run/manual-only mode.
- Polyglot Body runs in Python-only fallback. Compile/test lifecycles are unwired.

## Warnings
- System body is not fully complete (Body Score: 82.0% < 90%).

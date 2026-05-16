# Context Laplace Transform

DUMMIE uses context transform as an engineering metaphor. It is not a real mathematical Laplace transform, and this document must not be used as decorative mathematics.

## Time-Domain Context

Time-domain context includes chat history, agent reports, file changes, tests, errors, decisions, specs, memory, vault entries, phase outcomes, and mentor reviews.

## State-Domain Context

State-domain context includes objectives, phases, invariants, truth hierarchy, lifecycle state, context receipts, snowball metrics, next action, recovery packet, session contract, roadmap state, and capability state.

## Purpose

- reduce prompt noise;
- preserve global invariants;
- make long-term objectives operational;
- convert history into controllable state;
- prevent roadmap drift across CLI/IDE sessions.

## Operational Mapping

| Input Signal | Transformed State |
| --- | --- |
| user request | objective node |
| agent report | evidence candidate |
| test result | verification signal |
| spec change | contract update |
| file change | freshness invalidation |
| vault entry | reusable memory |
| phase outcome | snowball metric |
| mentor review | governance signal |

This transform is implemented through local documentation, schemas, contracts, manifests, state files, and parseable reports.


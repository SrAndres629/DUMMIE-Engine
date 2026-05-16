# DUMMIE PLAN V1 — P6.1 Polyglot Registry Classification Hardening

## Decision

PASS_WITH_WARNINGS

## Why This Was Needed

P6 created the canonical polyglot registry, but Elixir had mixed first-party and dependency/build evidence. Treating all Elixir as dependency would preserve the Python-only bias risk in another form.

## Corrections

- Elixir first-party evidence exists under `layers/l0_overseer/lib` and `layers/l0_overseer/test`.
- Dependency/build paths `layers/l0_overseer/deps` and `layers/l0_overseer/_build` are separated from first-party identity.
- TypeScript/JavaScript evidence in L6 was checked and remains dependency-only under `layers/l6_skin/node_modules`.
- Rust first-party evidence was confirmed under `layers/l3_shield/src/lib.rs`.

## Runtime Modification

Runtime code was not modified.

## P7 Impact

P7 must consume the corrected registry and must not collapse DUMMIE into Python-only or misclassify Elixir/TS dependency evidence as architecture identity.

## Next Phase

P7 — ProjectWorldModel

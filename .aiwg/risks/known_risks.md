# Known Risks — DUMMIE Engine

This logs all known technical risks and their operational mitigations.

---

## 1. RSK-001: Environment Induced Silent Fallback
* **Description**: Lost local dependencies (`numpy`, `fastembed`) when compiling workspace indexes, triggering silent fallback.
* **Mitigation**: Enforce strict execution using `layers/l2_brain/.venv/bin/python`, and keep regression gates inside test suites.

## 2. RSK-002: Local Model Heavy Inferences
* **Description**: Local models download large binaries, causing high latency or out of memory states.
* **Mitigation**: Enforce lightweight `bge-small-en-v1.5` and deterministically limit max candidate vectors to rerank.

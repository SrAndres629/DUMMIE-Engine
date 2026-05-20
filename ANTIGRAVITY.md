# Antigravity 2.0 Agent Collaboration Model

## Purpose
Define practical collaboration roles for multi-agent development under the Antigravity 2.0 runtime in this repository.

## Roles
1. `contract-architect`: define/validate interfaces and constraints.
2. `behavior-synth`: express acceptance tests and expected behavior.
3. `clean-coder-pro`: implement bounded changes.
4. `formal-validator`: run checks and report evidence.
5. `context-memory-manager`: keep decision trace and session continuity.

## Execution Rules
- **Environment:** ALWAYS use the centralized virtual environment. Prefix commands with `source .venv/bin/activate &&` or use `uv run`. Never use the global Python interpreter.
- Spec-first for high-impact changes.
- Small diffs with explicit ownership.
- Verification evidence required before completion claims.
- Update docs when assumptions or architecture claims change.
- **Antigravity standard:** All workspace configuration and metadata are stored in the `.agents/` folder.
- **Engineering Manifest:** Adhere to the standards defined in `.agents/manifests/ANTIGRAVITY_2_0_ENGINEERING_MANIFEST.md`.


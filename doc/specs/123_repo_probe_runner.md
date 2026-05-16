# Spec 123: Repo Probe Runner

## Purpose
Ground the DUMMIE engine's world model in physical evidence by deterministic inspection of the repository structure, layers, languages, specs, and tests.

## Scope
- Layer inspection (L0-L6).
- Polyglot language mapping.
- Spec triplet validation (.md, .feature, .rules.json).
- Critical runtime module presence.
- State coherence guard integration.

## Runtime Behavior
1. Use `git ls-files` to gather a list of all tracked files.
2. Analyze file paths to determine layer presence and language distribution.
3. Check for the existence of critical files in `layers/l2_brain/`.
4. Validate that each spec in `doc/specs/` has its corresponding `.feature` and `.rules.json`.
5. Read the latest `state_coherence_guard` report to ensure local consistency.
6. Produce `repo_probe_latest.json`.

## Safety Rules
- Do not read entire file contents; use metadata and path analysis.
- Do not include secrets or API keys in evidence.
- Do not modify any files.

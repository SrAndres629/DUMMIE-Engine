# Restart Validation Protocol

Restart validation means:

1. close current agent context or simulate cold-read;
2. reload current_position.json;
3. reload next_phase_seed.json;
4. reload phases.yaml;
5. verify P2 can be selected without chat memory;
6. verify reports are discoverable;
7. verify session contracts are discoverable.

Phase 1 may validate restart through cold-read simulation. A real laptop restart is not required for this phase.

Minimum Phase 1 evidence:

- `.aiwg/evolution/current_position.json` loads and names P1.
- `.aiwg/evolution/next_phase_seed.json` loads and names P2.
- `.aiwg/evolution/phases.yaml` registers 31 phases.
- `.aiwg/session_contracts/` contains the universal, Gemini CLI, Codex CLI, and Antigravity IDE contracts.


# Universal Agent Session Contract

Every DUMMIE Engine agent session must:

1. Read `.aiwg/evolution/current_position.json`.
2. Read `.aiwg/evolution/next_phase_seed.json`.
3. Review forbidden skips.
4. Execute reality lock.
5. Avoid broad repo reads.
6. Reuse existing DUMMIE capabilities when they apply.
7. Produce evidence.
8. Produce MD and JSON reports.
9. Update only within scope.
10. Not redefine roadmap from chat memory.
11. Not store private chain-of-thought.
12. Not store secrets.

The agent must not redefine the roadmap from chat memory.

The agent must load the canonical roadmap from `.aiwg/evolution/`.

Required first files:

- `.aiwg/evolution/current_position.json`
- `.aiwg/evolution/next_phase_seed.json`
- `.aiwg/evolution/phases.yaml`
- `.aiwg/evolution/phase_dependencies.graph.json`

Authority defaults:

- A0: reading, analysis, reports.
- A1: scoped repo edits.
- A2-A5: require explicit escalation request unless a phase contract explicitly authorizes the action.


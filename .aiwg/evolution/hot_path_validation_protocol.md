# Hot-Path Validation Protocol

Hot-path validation means:

1. agent starts from current_position.json;
2. agent reads next_phase_seed.json;
3. agent determines P2 is next;
4. agent refuses forbidden skip;
5. agent can explain required P2 outputs;
6. agent can locate session contracts.

Phase 1 hot-path validation is a file-discovery and state-selection check. It does not start P2, mutate runtime modules, activate swarm, or perform Kuzu writes.


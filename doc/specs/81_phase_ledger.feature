Feature: Phase Ledger
  As a long-running mission runtime
  I want phase events recorded in an append-only ledger
  So that current state can be reconstructed after context loss

  Scenario: mission history is append-only
    Given a mission has phase events
    Then `phase_ledger.jsonl` preserves each event as a separate JSON line

  Scenario: current state is reconstructed
    Given a ledger with mission and phase lifecycle events
    Then `current_state.json` can be rebuilt from the JSONL history

  Scenario: recovery artifacts are public
    Given a checkpoint or recovery packet payload
    Then private chain-of-thought and secret references are rejected

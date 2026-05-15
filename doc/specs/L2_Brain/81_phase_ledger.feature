Feature: Phase Ledger
  As a long-running mission runtime
  I want phase events recorded in an append-only ledger
  So that current state can be reconstructed after context loss

  Scenario: mission history is append-only
    Given a mission has phase events
    Then `phase_ledger.jsonl` preserves each event as a separate JSON line
    And Performance Metric: latency < 100ms

  Scenario: current state is reconstructed
    Given a ledger with mission and phase lifecycle events
    Then `current_state.json` can be rebuilt from the JSONL history
    And Performance Metric: latency < 100ms

  Scenario: recovery artifacts are public
    Given a checkpoint or recovery packet payload
    Then private chain-of-thought and secret references are rejected
    And Performance Metric: latency < 100ms
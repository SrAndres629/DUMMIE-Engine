Feature: Strategic Partner Swarm
  As a Cognitive Architect
  I want a multi-role advisory layer
  So that mission decisions are reviewed from multiple specialized perspectives.

  Scenario: Swarm review of a coherent mission
    Given all coherence guards report "PASS"
    When the StrategicPartnerSwarm runs
    Then the decision should be "continue_next_phase"
    And all 6 roles should be present in the report.

  Scenario: Swarm review of an incoherent mission
    Given MissionCoherenceGuard reports "FAIL"
    When the StrategicPartnerSwarm runs
    Then the decision should be "block_due_to_coherence_failure"
    And the Critic role should report an objection.

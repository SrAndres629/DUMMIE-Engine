Feature: Context Packet Optimizer
  As a Token Economy Optimizer,
  I want to compare multiple context assembly strategies,
  So that DUMMIE selects a compressed representation that maximizes evidence integrity while minimizing token usage.

  Scenario: Optimization selects the most token-efficient strategy
    Given a compiled 6D context packet and its intent
    When the context packet optimizer runs
    Then it should compare raw scanning vs 6D context compaction
    And it should select a strategy with a reduction ratio greater than 1.0
    And it should verify that required evidence is preserved
    And it should set the decision to PASS and save the optimization reports

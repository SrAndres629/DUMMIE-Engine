Feature: Meta-Gateway Sensor-First Policy
  Scenario: Blocking direct read for discovery without prior gateway search
    Given a concept discovery request
    And no prior gateway or semantic search
    When the policy is evaluated
    Then the decision should be WARN or BLOCK

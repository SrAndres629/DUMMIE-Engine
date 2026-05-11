Feature: Runtime Token Economy
  Scenario: Recording token usage
    Given a valid usage event
    When the TokenCostLedger records the event
    Then it should be queryable by session and mission
    And the total cost should reflect the new input

  Scenario: Budget enforcement
    Given a mission with a 10k token budget
    And a context packet of 12k tokens
    When the ContextBudgetManager evaluates the packet
    Then it should recommend compression or truncation

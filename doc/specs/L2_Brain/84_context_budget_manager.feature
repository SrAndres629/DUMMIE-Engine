Feature: Context Budget Manager

  Scenario: Enforce budget by dropping low priority items
    Given a context budget of 1000 tokens
    And context items totaling 1200 tokens
    When I enforce the budget
    Then all "critical" items should be preserved
    And Performance Metric: latency < 100ms
    And "low" priority items should be discarded until the budget is met
    And a budget pressure summary should be returned
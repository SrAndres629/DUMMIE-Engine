Feature: Debate & Adversarial Review Runtime
  As a Strategic Auditor
  I want to challenge mission plans through multiple specialized roles
  So that I can identify contradictions and evidence gaps before execution.

  Scenario: Plan accepted with minor observations
    Given MissionCoherenceGuard reports "PASS"
    And MissionPlan contains tests for all modules
    When the DebateReviewRuntime runs
    Then the decision should be "accept_plan"
    And all 6 roles should be present in the report.

  Scenario: Blocked due to coherence failure
    Given MissionCoherenceGuard reports "FAIL"
    When the DebateReviewRuntime runs
    Then the decision should be "block"
    And the Mentor Judge verdict should be "block".

Feature: Mission Workbench Manager

  Scenario: Create and populate a mission workbench
    Given a mission with ID "m1" and goal "Refactor Engine"
    When I create a workbench for mission "m1"
    Then the directory ".aiwg/workbench/m1/" should contain "objective.md"
    And "token_budget.json" should be generated
    And the workbench status should be "active"

  Scenario: Record a decision in the workbench
    Given an active workbench for mission "m1"
    When I append a decision "Use JSONL for logs"
    Then "decision_log.jsonl" should contain the decision event

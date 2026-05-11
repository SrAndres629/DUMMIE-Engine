Feature: Mission Workbench
  Scenario: Initializing a new workbench
    Given a new mission with ID "m123" and goal "refactor code"
    When the MissionWorkbenchManager creates the workbench
    Then a directory ".aiwg/workbench/m123/" should exist
    And an "objective.md" file should be present

  Scenario: Preventing path traversal
    Given an active workbench "m123"
    When an attempt is made to write an artifact to "../../etc/passwd"
    Then the operation must be blocked with an error

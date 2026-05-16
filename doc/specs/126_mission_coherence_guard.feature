Feature: Mission Coherence Guard
  As a Mission Coherence Auditor
  I want to detect when mission artifacts reflect stale phases
  So that DUMMIE Engine does not operate on inconsistent plans.

  Scenario: Detect P23 drift when in P26
    Given roadmap next_phase is "P26"
    And "mission_plan_latest.json" reflects "MISSION_P23"
    When the MissionCoherenceGuard runs
    Then the decision should be "FAIL"
    And a Mission ID mismatch finding should be recorded.

  Scenario: Pass when coherent
    Given roadmap next_phase is "P26"
    And "mission_plan_latest.json" reflects "MISSION_P26"
    And "mission_orchestrator_dag_latest.json" reflects "MISSION_P26"
    When the MissionCoherenceGuard runs
    Then the decision should be "PASS"

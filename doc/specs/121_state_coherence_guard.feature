Feature: State Coherence Guard
  As a Cognitive Runtime Engineer
  I want to detect when latest reports reflect stale phases
  So that DUMMIE Engine does not operate on inconsistent information.

  Scenario: All artifacts are coherent
    Given canonical current_phase is "P21" and next_phase is "P22"
    And "cli_control_plane_latest.json" reports "P21" and "P22"
    And "process_monitor_latest.json" reports "P21" and "P22"
    When StateCoherenceGuard runs
    Then the decision should be "PASS"
    And no ERROR findings should be present.

  Scenario: Artifact phase mismatch
    Given canonical current_phase is "P21" and next_phase is "P22"
    And "dashboard_l6_latest.json" reports "P18" and "P19"
    When StateCoherenceGuard runs
    Then the decision should be "FAIL"
    And an ERROR finding for "dashboard_l6_latest.json" should be recorded.

  Scenario: Missing optional artifact
    Given canonical current_phase is "P21" and next_phase is "P22"
    And "dashboard_l6_latest.html" is missing
    When StateCoherenceGuard runs
    Then the decision should be "PASS_WITH_WARNINGS"
    And a WARNING finding for "dashboard_l6_latest.html" should be recorded.

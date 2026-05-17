Feature: Whole-Body Scanner, Wiring Matrix, and Shadow Detector

  As a strategic metacognitive architect,
  I want to run a complete systemic audit of repository assets,
  So that I can identify shadow modules, unmapped specs, orphaned tests, and stale reports.

  Scenario: Auditing workspace modules and dependencies
    Given a workspace containing python files, specs, schemas, and reports
    When a whole-body scan is executed
    Then it should calculate a systemic coherence score
    And it should identify unimported python modules with no specs as orphaned shadow modules
    And it should list orphaned tests, unvalidated specs, and stale reports
    And it should write outputs to whole_body_scan_latest.json and whole_body_scan_latest.md

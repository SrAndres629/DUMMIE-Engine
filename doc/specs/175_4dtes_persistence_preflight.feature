Feature: 4D-TES Persistence Preflight
  As a Cognitive Systems Architect,
  I want to safely inspect the Kùzu database integrity,
  So that DUMMIE flags persistence issues without corrupting graph files.

  Scenario: Auditing degraded Kùzu configuration
    Given a degraded or unconfigured Kùzu/4D-TES persistence environment
    When the preflight runtime executes
    Then it should set decision to PASS_WITH_WARNINGS
    And it should set graph_write_mode to READY or REPAIRING
    And it should compile a non-destructive repair plan and write preflight reports

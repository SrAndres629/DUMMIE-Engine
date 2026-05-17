Feature: Wiring Matrix Builder
  As a Metacognitive Runtime Engineer,
  I want to construct a complete structural dependency map,
  So that I can identify specs and modules that are disconnected.

  Scenario: Builder maps standard relationships
    Given a scanned workspace database
    When the wiring matrix builder runs
    Then it should build directed edges representing imports
    And it should identify which source files are mapped to tests
    And it should identify specs with no source code
    And it should save the graph as wiring_matrix_latest.json

  Scenario: Builder detects missing test coverage
    Given a module that has no matching test file in the workspace
    When the wiring matrix builder runs
    Then it should include this module in source_without_tests

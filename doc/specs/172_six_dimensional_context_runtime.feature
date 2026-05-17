Feature: Six-Dimensional Context Runtime
  As a Metacognitive Runtime Engineer,
  I want to assemble raw scan results into structured, multidimensional context packets,
  So that the DUMMIE Engine receives a surgical, high-value, and resource-bounded context window.

  Scenario: Assembly of a comprehensive 6D context packet
    Given a fresh whole-body scanner execution report and active intent
    When the 6D context runtime builds a context packet
    Then it should compile items across all six axes
    And it should compute token budgets and verify evidence references
    And it should output a status of PASS
    And it should write the 6D context report files

  Scenario: Inclusion of stale reports triggers PASS_WITH_WARNINGS
    Given a context builder run involving reports older than 24 hours
    When the 6D context runtime builds the context packet
    Then it should flag the stale items
    And it should set the decision to PASS_WITH_WARNINGS

Feature: Repo Intelligence Query
  As a Developer
  I want to query the repository state
  So that I can find specific files without manual searching.

  Scenario: Find untested runtime
    When querying for "no_tests" and "is_runtime"
    Then the result should contain runtime files lacking corresponding tests.

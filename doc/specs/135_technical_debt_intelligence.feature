Feature: Technical Debt Intelligence
  As a Technical Debt Architect
  I want to find gaps in the codebase
  So that I can prioritize refactoring.

  Scenario: Detect missing test
    When a runtime file has no corresponding test
    Then TechnicalDebtIntelligence should create a finding
    And add it to the integration backlog.

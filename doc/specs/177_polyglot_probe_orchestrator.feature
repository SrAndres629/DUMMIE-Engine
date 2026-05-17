Feature: Polyglot Probe Orchestrator
  As a Polyglot Runtime Integrator,
  I want to scan and index active workspace programming languages,
  So that DUMMIE avoids Python-only bias and maps polyglot components safely.

  Scenario: Auditing a multi-language codebase manifest
    Given an active multi-language workspace with manifest files
    When the polyglot probe runs
    Then it should count first-party modules and locate manifest settings
    And it should respect exclusions (node_modules, target, .venv)
    And it should output a decision of PASS and write the polyglot probe reports

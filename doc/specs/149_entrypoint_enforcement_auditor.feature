Feature: Entrypoint Enforcement Audit
  Scenario: Detect missing integrations
    Given a set of known entrypoints
    When the auditor runs
    Then each entrypoint must be audited for context gate, memory spine, outcome, and token cost
    And the decision must be PASS_WITH_WARNINGS if any entrypoint lacks memory spine

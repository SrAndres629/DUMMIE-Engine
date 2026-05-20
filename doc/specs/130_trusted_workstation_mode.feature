Feature: Trusted Workstation Mode
  As a Workstation Guardian
  I want to classify and gate local actions
  So that I can prevent unsafe or unauthorized operations on the host machine.

  Scenario: Deny obsolete read-only action
    Given a request for "READ_ONLY_STATUS"
    When evaluated by TrustedWorkstationMode
    Then the decision should be "DENY"
    And reason should mention obsolete category.

  Scenario: Allow active analyze and plan action
    Given a request for "ANALYZE_PLAN"
    When evaluated by TrustedWorkstationMode
    Then the decision should be "ALLOW"
    And can_execute_now should be true.

  Scenario: Block env access
    Given a request targeting ".env"
    When evaluated by TrustedWorkstationMode
    Then the decision should be "BLOCK"
    And reason should mention policy violation.

  Scenario: Allow workspace write with verification
    Given a request for "WORKSPACE_WRITE"
    And verification evidence is attached
    When evaluated by TrustedWorkstationMode
    Then the decision should be "ALLOW_WITH_VERIFICATION"
    And can_execute_now should be true.

Feature: Trusted Workstation Mode
  As a Workstation Guardian
  I want to classify and gate local actions
  So that I can prevent unsafe or unauthorized operations on the host machine.

  Scenario: Allow safe read-only action
    Given a request for "READ_ONLY_STATUS"
    When evaluated by TrustedWorkstationMode
    Then the decision should be "ALLOW"
    And can_execute_now should be true.

  Scenario: Block env access
    Given a request targeting ".env"
    When evaluated by TrustedWorkstationMode
    Then the decision should be "BLOCK"
    And reason should mention policy violation.

  Scenario: Require approval for workspace edit
    Given a request for "WORKSPACE_EDIT"
    When evaluated by TrustedWorkstationMode
    Then the decision should be "ALLOW_WITH_HUMAN_APPROVAL"
    And requires_authorization should be true.

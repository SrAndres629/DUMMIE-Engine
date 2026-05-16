Feature: Mission Autonomy Contract
  As a Governance Engine
  I want to evaluate and gate agentic requests against a strict authority contract
  So that I can prevent unsafe actions and unauthorized workspace mutations.

  Scenario: Allow safe advisory request
    Given DebateReview reports "accept_plan"
    And requested scope is "ADVISORY_ONLY"
    When the MissionAutonomyContract evaluates the request
    Then the decision should be "ALLOW"
    And can_execute_now should be true.

  Scenario: Deny credential access
    Given a request for scope "READ_ONLY_ANALYSIS" targeting ".env"
    When the MissionAutonomyContract evaluates the request
    Then the decision should be "BLOCK"
    And the reason should mention credentials/env access forbidden.

  Scenario: Require human approval for mutation
    Given requested scope is "HUMAN_APPROVED_WORKSPACE_EDIT"
    When the MissionAutonomyContract evaluates the request
    Then the decision should be "ALLOW_WITH_HUMAN_APPROVAL"
    And "human_approval" should be in required_authorizations.

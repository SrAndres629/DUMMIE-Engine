Feature: Mission Autonomy Contract
  As a Governance Engine
  I want to evaluate and gate agentic requests against a strict authority contract
  So that I can prevent unsafe actions and unauthorized workspace mutations.

  Scenario: Allow active analyze and plan request
    Given DebateReview reports "accept_plan"
    And requested scope is "ANALYZE_PLAN"
    When the MissionAutonomyContract evaluates the request
    Then the decision should be "ALLOW"
    And can_execute_now should be true.

  Scenario: Deny obsolete read-only analysis
    Given a request for scope "READ_ONLY_ANALYSIS"
    When the MissionAutonomyContract evaluates the request
    Then the decision should be "DENY"
    And the reason should mention obsolete scope.

  Scenario: Deny credential access
    Given a request for scope "ANALYZE_PLAN" targeting ".env"
    When the MissionAutonomyContract evaluates the request
    Then the decision should be "BLOCK"
    And the reason should mention credentials/env access forbidden.

  Scenario: Allow workspace write with verification evidence
    Given requested scope is "WORKSPACE_WRITE"
    And verification evidence is attached
    When the MissionAutonomyContract evaluates the request
    Then the decision should be "ALLOW_WITH_VERIFICATION"
    And "verification_required" should be in required_authorizations.

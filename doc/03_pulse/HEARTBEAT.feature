Feature: Operational Heartbeat Tasks
  As a system operator
  I want periodic lightweight checks
  So that drift and risk are detected early

  Scenario: heartbeat runs integrity checks
    Given heartbeat is enabled
    When a pulse executes
    Then documentation and basic system checks are evaluated

  Scenario: heartbeat records outcome
    Given a pulse finished
    When result is produced
    Then outcome is recorded for follow-up actions

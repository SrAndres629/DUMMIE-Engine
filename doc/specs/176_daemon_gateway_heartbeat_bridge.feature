Feature: Daemon/Gateway Heartbeat Bridge
  As a Gateway Wiring Engineer,
  I want to wrap system operations in a human-gated dispatch envelope,
  So that no background daemon or gateway forks can execute code modifications autonomously.

  Scenario: Preparing dispatch envelope for a mutation action
    Given a decision policy selecting a mutation or repair action
    When the daemon/gateway bridge compiles the dispatch envelope
    Then it must set requires_human_approval to true
    And it must set can_execute_now to false
    And the target must be human_review or antigravity
    And it should save the bridge reports conforming to the schema

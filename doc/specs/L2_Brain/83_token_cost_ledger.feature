Feature: Token Cost Ledger

  Scenario: Record and summarize mission cognitive costs
    Given a mission with ID "m1"
    When I record a usage event for mission "m1" with 100 input tokens and 50 output tokens
    Then the mission summary for "m1" should show 150 total tokens
    And Performance Metric: latency < 100ms
    And the ledger should contain 1 event

  Scenario: Idempotency by event_id
    Given a session with ID "s1"
    And an event with ID "evt1"
    When I record the event "evt1" twice
    Then the session ledger should only contain 1 event
    And Performance Metric: latency < 100ms
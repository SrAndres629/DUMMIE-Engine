Feature: Runtime Lifecycle Chat Contract
  As a DUMMIE operator
  I want chat to run through runtime lifecycle orchestration
  So that preprocessing, routing, provider selection, and traceability are always explicit

  Scenario: Chat call executes runtime pipeline
    Given a user prompt for dummie chat
    When the runtime executes
    Then preprocessing metadata should be produced
    And a routing tier and model decision should be produced
    And a provider selection should be recorded

  Scenario: Chat call writes traceability artifacts
    Given a successful chat call
    When the runtime finishes
    Then runtime_chat_latest.json should exist
    And runtime_chat_trace_latest.json should exist
    And a runtime-chat receipt should be written

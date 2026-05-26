Feature: Shared Memory Gateway IPC
  As a DUMMIE Engine operator
  I want large payloads between MetaGateway and sub-gateways to use shared memory
  So that serialization overhead is minimized

  Scenario: Small payload uses HTTP (default path)
    Given a payload <64KB
    When MetaGateway calls a sub-gateway tool
    Then the payload is sent via HTTP POST

  Scenario: Large payload uses memfd
    Given a payload >64KB
    When MetaGateway calls a sub-gateway tool
    Then the payload is written to a memfd
    And the sub-gateway reads from the memfd
    And the memfd is sealed after writing

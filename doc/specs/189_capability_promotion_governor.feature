Feature: Capability Promotion Governor
  As a Metacognitive Security Gatekeeper,
  I want to evaluate capability telemetry reports,
  So that DUMMIE prevents false status promotions and enforces the physical truth.

  Scenario: Auditing and gating capability status promotion
    Given telemetry reports for Kùzu, embeddings, and dependencies
    When the capability promotion governor evaluates status changes
    Then it should decide whether promotion to READY is allowed for each capability
    And it should block promotion to READY if dependencies are not declared in pyproject.toml
    And it should write the latest capability promotion reports

Feature: Daemon Telemetry & Outcome Contracts
  As an agentic runtime
  I want daemon outcomes to use one stable contract
  So that long-running missions can be measured, resumed, and validated

  Scenario: frontmatter is complete
    Given the spec file `50_daemon_telemetry_contracts.md`
    Then it defines `spec_id`, `title`, `status`, `layer`, and `last_verified_on`

  Scenario: outcome fields are canonical
    Given a daemon outcome
    Then it includes mission, phase, route, metacognition, sensor-first, efficiency, evidence, next action, and recovery fields

  Scenario: mission runtime contract is resume-safe
    Given a mission runtime contract
    Then it rejects path traversal identifiers and generates a deterministic resume token

  Scenario: no private reasoning is serialized
    Given daemon outcome and mission runtime payloads
    Then public JSON output does not contain private chain-of-thought references

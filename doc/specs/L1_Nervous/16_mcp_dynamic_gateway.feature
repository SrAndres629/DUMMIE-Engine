Feature: MCP Dynamic Gateway contract
  As an engineering team
  I want this spec to stay aligned with physical implementation
  So that agents and humans operate with low-entropy context

  Scenario: frontmatter is complete
    Given the spec file `16_mcp_dynamic_gateway.md`
    Then it defines `spec_id`, `title`, `status`, `layer`, and `last_verified_on`
    And Performance Metric: latency < 100ms

  Scenario: evidence points to existing system areas
    Given the physical evidence section
    Then it references active repository paths for layer `L1`
    And Performance Metric: latency < 100ms

  Scenario: lifecycle is explicit
    Given this spec status is `ACTIVE`
    Then implementation and roadmap expectations are unambiguous
    And Performance Metric: latency < 100ms
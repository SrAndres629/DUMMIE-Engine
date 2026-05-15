Feature: Nodos Atómicos y Modularidad Plug & Play contract
  As an engineering team
  I want this spec to stay aligned with physical implementation
  So that agents and humans operate with low-entropy context

  Scenario: frontmatter is complete
    Given the spec file `23_atomic_modular_nodes.md`
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
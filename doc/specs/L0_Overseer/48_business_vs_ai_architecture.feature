Feature: Bifurcación de Arquitectura: Negocio vs IA contract
  As an engineering team
  I want this spec to stay aligned with physical implementation
  So that agents and humans operate with low-entropy context

  Scenario: frontmatter is complete
    Given the spec file `48_business_vs_ai_architecture.md`
    Then it defines `spec_id`, `title`, `status`, `layer`, and `last_verified_on`
    And Performance Metric: latency < 100ms

  Scenario: evidence points to existing architecture artifacts
    Given the physical evidence section
    Then it references active repository paths for layer `L0`
    And Performance Metric: latency < 100ms
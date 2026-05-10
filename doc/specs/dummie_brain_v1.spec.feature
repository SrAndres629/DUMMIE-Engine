Feature: DUMMIE Brain MCP Specification v1.0 contract
  As an engineering team
  I want this spec to stay aligned with physical implementation
  So that agents and humans operate with low-entropy context

  Scenario: frontmatter is complete
    Given the spec file `dummie_brain_v1.spec.md`
    Then it defines `spec_id`, `title`, `status`, `layer`, and `last_verified_on`

  Scenario: evidence points to active gateway artifacts
    Given the physical evidence section
    Then it references active repository paths for layer `L1`

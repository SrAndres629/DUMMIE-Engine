Feature: Path Normalization & Industrial Environment contract
  As an engineering team
  I want this spec to stay aligned with physical implementation
  So that agents and humans operate with low-entropy context

  Scenario: frontmatter is complete
    Given the spec file `47_path_normalization.md`
    Then it defines `spec_id`, `title`, `status`, `layer`, and `last_verified_on`

  Scenario: evidence points to runtime path contracts
    Given the physical evidence section
    Then it references active repository paths for layer `L0`

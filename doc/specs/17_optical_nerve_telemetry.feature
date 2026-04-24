Feature: Nervio Óptico (Visualización 4D) contract
  As an engineering team
  I want this spec to stay aligned with physical implementation
  So that agents and humans operate with low-entropy context

  Scenario: frontmatter is complete
    Given the spec file `17_optical_nerve_telemetry.md`
    Then it defines `spec_id`, `title`, `status`, `layer`, and `last_verified_on`

  Scenario: evidence points to existing system areas
    Given the physical evidence section
    Then it references active repository paths for layer `L6`

  Scenario: lifecycle is explicit
    Given this spec status is `DRAFT`
    Then implementation and roadmap expectations are unambiguous

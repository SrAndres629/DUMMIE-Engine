Feature: Repo Probe Runner
  As a Runtime Architect
  I want to inspect the repository's physical state
  So that the system's world model is grounded in evidence.

  Scenario: Full repo scan
    Given a git repository with multiple layers and specs
    When the RepoProbeRunner executes
    Then it should detect present layers from L0 to L6
    And it should identify language distribution
    And it should detect incomplete spec triplets.

Feature: Repo Intelligence Runtime
  As a Context Cartographer
  I want to scan and classify all tracked files
  So that the system knows what exists without reading everything.

  Scenario: Scan and classify
    Given a tracked Python file in layers/l2_brain
    When the RepoIntelligenceRuntime runs
    Then the file should be classified as "runtime"
    And its layer should be "l2_brain".

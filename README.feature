Feature: Repository Documentation Integrity
  As a maintainer
  I want README to reflect the current physical system state
  So that agents and engineers use accurate context

  Scenario: README states verifiable architecture
    Given the repository root
    When a reader reviews README.md
    Then layer responsibilities must map to existing paths

  Scenario: README avoids legacy claims
    Given historical project narratives
    When README is updated
    Then only current, verifiable context is kept

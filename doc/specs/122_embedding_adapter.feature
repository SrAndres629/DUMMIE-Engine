Feature: Embedding Adapter
  As a Semantic Systems Architect
  I want a stable embedding interface with offline fallback
  So that DUMMIE Engine can perform vector operations without API keys.

  Scenario: Deterministic fallback embedding
    Given text content "DUMMIE Engine"
    When I request a fallback embedding
    Then I should receive a 128-dimensional normalized vector
    And the same text should produce the exact same vector.

  Scenario: Cosine similarity
    Given two similar texts "DUMMIE Engine" and "DUMMIE Engine"
    When I calculate their similarity
    Then the result should be 1.0.

  Scenario: Provider disabled by default
    Given I request a "provider" embedding without configuration
    When the adapter runs
    Then the status should be "PROVIDER_DISABLED".

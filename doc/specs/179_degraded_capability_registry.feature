Feature: Degraded Capability Registry
  As a Metacognitive System Integrity Guardian,
  I want to consolidate all simulated and degraded states into a single registry,
  So that the cognitive loop operates with total systemic awareness.

  Scenario: Consolidation of capability states
    Given the latest dependency audit and preflight JSON reports
    When the degraded capability registry compiles all capabilities
    Then it should register kuzu_4dtes_persistence and real_semantic_embeddings
    And it should identify their actual status as DEGRADED or FALLBACK
    And it should record the blocks and reasons
    And it should output a decision of PASS_WITH_WARNINGS if critical modules are degraded
    And it should write the latest capability registry reports

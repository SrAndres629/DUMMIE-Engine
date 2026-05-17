Feature: Runtime Dependency Auditor
  As a Metacognitive Dependency Engineer,
  I want to safely audit python libraries and capability modes,
  So that DUMMIE has an honest map of what is physically importable and what is simulated.

  Scenario: Execution of dependency reality audit
    Given a clean python environment running under the L2 cerebro
    When the runtime dependency auditor runs
    Then it should check imports of kuzu, pytest, yaml, networkx
    And it should detect the absence of kuzu and flag its capability as DEGRADED or MISSING
    And it should classify deterministic embedding fallback as FALLBACK
    And it should output a decision of PASS_WITH_WARNINGS if optional dependencies are missing
    And it should write the latest dependency reports

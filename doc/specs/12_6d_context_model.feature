Feature: Modelo Formal de Memoria 6D-Context (DE-V2-L2-12)
  Criterios de Aceptación Ejecutables para el Contexto 6D.

  Scenario: Authority-Based Mutation Check (D6)
    Given an agent with "AuthorityLevel: MINOR"
    When the agent attempts to mutate a vector with "a = MAJOR"
    Then the SDD Shield must block the operation
    And an "Authority_Violation" log must be emitted to OTel
    And Performance Metric: authority_check_latency < 5ms

  Scenario: Selective Context Injection (D5)
    Given a context buffer with a threshold w = 0.7
    And a set of memory nodes with weights [0.9, 0.8, 0.5, 0.2]
    When the system performs a "Focus Injection"
    Then only nodes with w >= 0.7 must be injected into the LLM context
    And Performance Metric: injection_overhead < 100ms

  Scenario: Causal Immutability Enforcement (D1-D4)
    Given a collapsed reasoning branch
    When an agent attempts to modify a vector in D1, D2, D3, or D4
    Then the system must reject the mutation
    And the state must remain unchanged
    And Performance Metric: immutability_validation < 2ms

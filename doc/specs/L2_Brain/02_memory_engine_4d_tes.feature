Feature: Motor de Memoria Inmutable (DE-V2-L2-02)
  Criterios de Aceptación Ejecutables para el Sistema 4D-TES.

  Scenario: Enforce Lamport Causality
    Given a new event in the system
    And the current global tick is 500
    When the event is persisted to the "Episodic Memory" (Redb)
    Then its "lamport_tick" must be >= 501
    And all sibling agents must acknowledge the new tick before the next transition
    And Performance Metric: tick_propagation_latency < 50ms

  Scenario: Algebraic Branch Fusion (Join Operation)
    Given two concurrent reasoning branches "A" and "B"
    When the system executes a "Join (v)" operation
    Then the resulting LST must be the Least Upper Bound (LUB)
    And if an ambiguity is detected, an "Ambiguity_Ticket" must be emitted
    And Performance Metric: branch_fusion_time < 200ms

  Scenario: Memory Decay and Entropy Hard-Cap
    Given a memory node with entropy > 2.5 bits
    When the "Muscle (L5)" evaluator detects the breach
    Then L5 must trigger a "Compresión Asimétrica (Zstd SIMD)"
    And the node's semantic weight (W) must be normalized
    And Performance Metric: compression_latency < 10ms

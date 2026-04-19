Feature: Arquitectura Políglota de 7 Capas (DE-V2-L0-03)
  Criterios de Aceptación Ejecutables para el Swarm de Agentes.

  Scenario: Transition from PLANNING to VALIDATION
    Given an agent in "PLANNING" state (L2 - Python)
    And a formal code proposal is generated
    When the agent requests transition to "VALIDATION"
    Then the "Executive Arbiter" (L0 - Elixir) must verify the isolation rule
    And the proposal must be passed to "L3 - Shield" (Rust)
    And Performance Metric: transition_latency < 25ms

  Scenario: Enforce Memory Ownership (FEI Model)
    Given an "L3 - Shield" process as the MemoryOwner
    When an "L2 - Brain" process attempts direct write to the pointer
    Then the Shield must block the operation
    And the system must emit a "VIO_HEX_001" fault signal
    And Performance Metric: violation_detection_latency < 1ms

  Scenario: Adaptive Heartbeat Time Dilation
    Given a system with a "load_factor" of 0.5
    When L1 Nervous System emits a heartbeat
    Then L0 Overseer must calculate a "DynamicTimeout" of 67.5s (45s * 1.5)
    And the agent must not be purged before the Dilated Timeout.
    And Performance Metric: calculation_overhead < 500us

Feature: Agente de Consistencia Semántica (DE-V2-L2-39)
  Criterios de Aceptación Ejecutables para la Sincronía del Ecosistema.

  Scenario: Propagate Spec Change to Code
    Given a validated change in "doc/specs/L1_Nervous/10_contracts.md"
    When the Synchronizer initiates a "Cascading_Update"
    Then it must identify affected microservices via Impact Analytics (Spec 31)
    And it must orquestrate the update of Protobuf stubs in the Coder swarm
    And Performance Metric: propagation_latency < 10s

  Scenario: Veto Inconsistent Code Refactor
    Given a manual code change that violates the "Spec-as-Source" invariant
    When the Consistency Agent detects the "Semantic_Drift"
    Then it must revert the code to match the Spec
    And it must require an "Official_Spec_Update" before re-applying the change
    And Performance Metric: drift_reversion_time < 2s

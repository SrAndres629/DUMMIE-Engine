Feature: A2A Discovery Protocol (DE-V2-L2-37)
  Criterios de Aceptación Ejecutables para el Descubrimiento entre Agentes.

  Scenario: Agent Capability Advertisement
    Given an agent "A" with "Skill: Protobuf_Optimization"
    When agent_A broadcasts its presence on "ao.v2.l2.brain.presence"
    Then the Orchestrator must register its "Functional_Signature"
    And other agents must be able to discover agent_A via a "Capability_Lookup"
    And Performance Metric: discovery_broadcast_latency < 100ms

  Scenario: Secure A2A Delegation
    Given agent "A" delegating a task to agent "B"
    When agent_B accepts the delegation
    Then an MCP Sidecar must be provisioned for the task execution
    And all interactions must be traced via the "trace_id"
    And Performance Metric: delegation_handshake < 500ms

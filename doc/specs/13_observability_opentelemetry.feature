Feature: Observabilidad Sistémica - OTel (DE-V2-L6-13)
  Criterios de Aceptación Ejecutables para el Sustrato de Observabilidad.

  Scenario: Trace ID Propagation (L1-L6)
    Given an "AgentIntent" initiated in L2
    When the intent triggers an RPC to L1 (Go) and then to L5 (Mojo)
    Then the "trace_id" must remain identical across all Spans
    And the L6 Visualizer must render the DAG of the transaction
    And Performance Metric: trace_propagation_overhead < 5us

  Scenario: Veto Logging Privacy (L3 Interception)
    Given a log message containing a "Toxic_Pattern" (e.g. Secret Key)
    When the log reaches the OTel Collector via L3 (Shield)
    Then the L3 Shield must sanitize the log or block the export
    And it must emit a "Privacy_Violation" alert
    And Performance Metric: log_sanitization_latency < 2ms

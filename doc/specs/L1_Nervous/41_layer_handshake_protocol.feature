Feature: Protocolo de Handshake y Mensajería (DE-V2-L1-41)
  Criterios de Aceptación Ejecutables para el Handshake y Compatibilidad ACP.

  Scenario: Successful ACP initialization
    Given an IDE client attempting an ACP connection
    When it emits an "agent/initialize" JSON-RPC message
    Then the Layer 1 Nervous system must validate the protocol version
    And it must negotiate a session ID with the L0 Overseer
    And the Performance Metric: handshake_latency < 15ms
    And the Performance Metric: message_throughput > 1000/s

  Scenario: Message normalization to Protobuf
    Given an incoming ACP message "textDocument/didOpen"
    When the Nervous system receives the JSON payload
    Then it must normalize the content into an "io.dummie.v2.Intent" Protobuf message
    And the schema mapping must be validated by the S-Shield
    And the Performance Metric: normalization_latency < 2ms

  Scenario: Connection recovery
    Given a dropped WebSocket connection in the ACP bridge
    When the reconnect ritual is triggered
    Then the system must resume the previous session context from L2 Memory
    And the Performance Metric: recovery_time < 50ms

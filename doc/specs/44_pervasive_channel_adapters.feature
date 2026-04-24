Feature: Pervasive Channel Adapters (DE-V2-L1-44)
  Criterios de Aceptación Ejecutables para el Swarm de Agentes y Gateways de Mensajería.

  Scenario: Route WhatsApp message to L2 Brain
    Given an authenticated WhatsApp device "PAH_MOBILE"
    When a message "Deploy Greenfield" is received by the L1 Gateway
    Then the message must be normalized to an "Intent" Protobuf
    And the intent must reach the L2 Brain router
    And the Performance Metric: message_latency < 50ms
    And the Performance Metric: processing_cost < 0.001 USD

  Scenario: Continuity across multiple channels
    Given an active session "AO-SES-441" initiated via "Telegram"
    When the user sends a follow-up via "WhatsApp"
    Then the L1 Gateway must map the request to the same "Session_ID"
    And the contextual memory must remain consistent
    And the Performance Metric: session_mapping_time < 10ms

  Scenario: Reject unauthenticated channel input
    Given an incoming message from an unregistered phone number "+123456789"
    When the L1 Adapter receives the payload
    Then the message must be dropped at the "Shield" boundary
    And a "Security_Event" must be logged in the Decision Ledger.

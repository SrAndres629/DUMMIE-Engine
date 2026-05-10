Feature: Secure Node Pairing Protocol (DE-V2-L3-45)
  Criterios de Aceptación Ejecutables para el Onboarding Soberano de Hardware.

  Scenario: Approve a new laptop node
    Given a connection request from "MacBook-Pro-LST"
    And the node is in "QUARANTINE" state
    When the PAH clicks "APPROVE" in the Command Canvas
    Then L3 must issue a valid "X-AO-Device-Token"
    And the node must transition to "AUTHORIZED" state
    And the Performance Metric: handshake_latency < 200ms
    And the Performance Metric: crypto_verification < 50ms

  Scenario: Block unauthorized remote node
    Given an unrecognized connection attempt from IP "192.168.1.50"
    When the L3 Shield evaluates the security policy
    And no manual approval is received within "60s"
    Then the connection must be terminated with code "1008" (Policy Violation)
    And the IP must be added to the temporary blocklist
    And the Performance Metric: rejection_time < 5ms

  Scenario: Re-authenticate with rotated token
    Given an authorized node with an expired token (24h+)
    When it attempts to send a heartbeats signal
    Then it must perform a background token rotation handshake
    And the Performance Metric: rotation_latency < 100ms

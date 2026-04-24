Feature: Escudos Anti-Ignorancia (DE-V2-L3-04)
  Criterios de Aceptación Ejecutables para el Sistema de Blindaje.

  Scenario: Veto structural violation (S-Shield)
    Given an L2 agent attempting to write "os.remove()" in a pure domain file
    And the S-Shield is active in L3 (Rust)
    When the Sentinel conducts the Symbol Audit
    Then the action must be blocked in real-time
    And a "S-Shield_Veto" signal must be emitted via NATS
    And Performance Metric: interception_latency < 5ms

  Scenario: Financial Circuit Breaker (E-Shield)
    Given a task budget of 0.50 USD
    When the cumulative token cost exceeds 0.51 USD
    Then the E-Shield must suspend the agent's inferencing capability
    And it must invoke the Arbitrator (L0) for a budget review
    And Performance Metric: cost_audit_frequency > 10Hz

  Scenario: Exfiltration Guard (L-Shield)
    Given an agent attempt to use "requests.post" to an external domain
    And the domain is not in the whitelist
    When the Inten-Audit Sidecar (L1) interceptor triggers
    Then the process must be quarantined
    And VRAM Sanitization (zeroing) must be executed
    And Performance Metric: quarantine_activation < 1s

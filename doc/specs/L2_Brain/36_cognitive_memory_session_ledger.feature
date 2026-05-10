Feature: Cognitive Memory Session Ledger (DE-V2-L2-36)
  Criterios de Aceptación Ejecutables para la Memoria de Sesión.

  Scenario: Persistent Thought-Chain Logging
    Given an agent performing a complex reasoning task
    When the agent generates an "Inference_Step"
    Then the step must be logged to ".aiwg/memory/session_ledger.jsonl"
    And the log must include the associated "lamport_tick"
    And Performance Metric: session_logging_latency < 50ms

  Scenario: Snapshot State for Recovery
    Given a session with 100+ inference steps
    When the system triggers a "Memory_Snapshot"
    Then it must compress the session ledger into a binary "Necro_Blob"
    And the current architecture state must be point-in-time recoverable
    And Performance Metric: snapshot_time < 2s

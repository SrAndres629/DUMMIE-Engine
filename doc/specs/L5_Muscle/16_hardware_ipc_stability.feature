Feature: Estabilidad IPC y Memoria Compartida (DE-V2-L5-16)
  Criterios de Aceptación Ejecutables para el Bus SHM.

  Scenario: Validate Binary Header Integrity
    Given an SHM buffer allocated by Layer 3 (Rust)
    When a process reads the 64B header
    Then it must find the magic "ATKN" at offset 0
    And the "TicketID" UUID must match the active transaction
    And Performance Metric: header_integrity_check < 100us

  Scenario: Zero-Copy Arrow Transmission
    Given a large telemetry set in L6
    When the system persists it to L5 SHM
    Then it must be transmitted via Apache Arrow without user-space copies
    And the "Data_Offset" must be 64-byte aligned
    And Performance Metric: transmission_bandwidth > 10GB/s

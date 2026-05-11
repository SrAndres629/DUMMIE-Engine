Feature: Motor de Ultra-Compresión del Multiverso (DE-V2-L5-32)
  Criterios de Aceptación Ejecutables para el Almacenamiento Multinivel.

  Scenario: Compression of Dead Branches
    Given a multiverse branch in state "REJECTED"
    And idle time > 100 ticks
    When the L5 Mojo compression kernel triggers
    Then the branch must be compressed using Zstd (Level 19-22)
    And the resulting blob must be stored in "/data/cold_storage/"
    And Performance Metric: compression_ratio > 10.0

  Scenario: Lazy-Decompression for Necro-Learning
    Given a compressed branch blob in cold storage
    When a L2 agent requests access for "Necro-Learning"
    Then the system must perform a Lazy-Decompression to RAM
    And the symbols must be temporarily re-injected into KùzuDB
    And Performance Metric: decompression_latency < 500ms

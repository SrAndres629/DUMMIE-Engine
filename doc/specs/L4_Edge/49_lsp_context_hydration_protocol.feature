Feature: Protocolo de Hidratación Semántica LSP (DE-V2-L4-49)
  Criterios de Aceptación Ejecutables para el Puente Semántico y la Hidratación de LST.

  Scenario: Hydrate context from a function symbol
    Given the user cursor is on line 42 of "main.go"
    When the L4 Edge Gateway requests "textDocument/documentSymbol" via ACP
    Then the agent context must be populated with the function signature and its immediate dependencies
    And the visual screenshot must be secondary to the LST data
    And the Performance Metric: semantic_hydration_latency < 20ms

  Scenario: Detect errors via LSP diagnostics
    Given a syntax error "unexpected semicolon" in the active file
    When the IDE emits a "textDocument/publishDiagnostics" event
    Then the agent must trigger a "Self-Healing" intent automatically
    And the Performance Metric: error_detection_latency < 5ms

  Scenario: Snapshot token optimization
    Given a large file of 2000 lines
    When the Semantic Bridge performs a skeletal extraction
    Then the resulting context payload must be < 20% of the raw file size
    And the agent must still be able to identify the "Aggregate Root" of the component
    And the Performance Metric: compression_ratio > 0.8

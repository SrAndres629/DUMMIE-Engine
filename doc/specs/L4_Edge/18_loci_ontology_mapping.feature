Feature: LST Ontology Mapping (DE-V2-L4-18)
  Criterios de Aceptación Ejecutables para el Mapeado LST en Zig.

  Scenario: Extract Symbols from Source Code
    Given a new source file "main.go"
    When the Layer 4 (Zig) scanner parses the file
    Then it must identify all symbols (Functions, Structs, Constants)
    And it must generate a Language Symbol Tree (LST)
    And Performance Metric: scanning_througput > 1000_lines/ms

  Scenario: Detect Architectural Violations in LST
    Given an LST containing a dependency from "Domain" to "Infrastructure"
    When the Sentinel audits the symbol tree against L0 topology
    Then it must flag a "Circular_Dependency" or "Layer_Violation"
    And Performance Metric: audit_time < 10ms

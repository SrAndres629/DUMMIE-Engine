Feature: Contratos Ejecutables de Gobernanza - SDD (DE-V2-L3-22)
  Criterios de Aceptación Ejecutables para el Sistema SDD.

  Scenario: Load and Enforce JSON Invariant
    Given a new rule file in "/governance/rules/VIO_HEX_001.json"
    When the L3 Shield (Rust) performs a "Bootstrap Load"
    Then the rule must be mmapped into protected memory
    And any L2 agent attempting to violate it must be blocked
    And Performance Metric: rule_load_latency < 10ms

  Scenario: Global Re-scan on Governance Patch
    Given a modified rule in the governance directory
    When the PAH (Human) confirms the "Sovereign Decree"
    Then the Shield must trigger a "Re-Scan Global" of the monorepo
    And any file that deviates must be marked as "CORRUPTED"
    And Performance Metric: scan_througput > 100_files/sec

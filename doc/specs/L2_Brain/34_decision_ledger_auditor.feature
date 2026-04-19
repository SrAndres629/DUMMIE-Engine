Feature: Decision Ledger Auditor (DE-V2-L2-34)
  Criterios de Aceptación Ejecutables para el Registro de Decisiones.

  Scenario: Log Sovereign Decision (PAH)
    Given a decision made by the Human Authority (PAH)
    When the Ledger Auditor receives the "Resolution_Signal"
    Then it must persist the decision to "/ledger/sovereign_resolutions.jsonl"
    And it must generate a "Knowledge Witness" hash linking to the Spec ID
    And Performance Metric: logging_latency < 100ms

  Scenario: Audit Agent Consistency against Ledger
    Given an agent proposing a change
    When the Auditor scans the "Decision Ledger" for contradictory past resolutions
    Then it must block the proposal if a "Sovereign_Veto" is found
    And it must emit a "Consistency_Violation" signal
    And Performance Metric: audit_scan_time < 200ms

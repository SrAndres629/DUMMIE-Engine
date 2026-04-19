Feature: Pipeline de Necro-Learning (DE-V2-L5-35)
  Criterios de Aceptación Ejecutables para el Aprendizaje de Fallos.

  Scenario: Extract Danger Nodes from Dead Branches
    Given a set of dead branches in "Cold Storage"
    When the Necro-Auditor executes a "Causal Necropsy"
    Then it must identify the "Danger Patterns" (conflicting symbols/traits)
    And it must inject these patterns as "Danger Nodes" in Layer 4 (KùzuDB)
    And Performance Metric: pattern_extraction_latency < 60s

  Scenario: Preventative Veto via Necro-Awareness
    Given a new agent intent that colides with a "Danger Node" (prob > 40%)
    When the Sentinel performs the pre-flight check
    Then the system must request a "Sovereign_Validation" from the PAH
    And the execution must be paused until approval
    And Performance Metric: risk_detection_time < 500ms

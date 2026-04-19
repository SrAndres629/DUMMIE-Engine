Feature: Refinamiento Kaizen Loop (DE-V2-L2-27)
  Criterios de Aceptación Ejecutables para la Mejora Continua.

  Scenario: Autonomous Error Learning
    Given a failed execution in the "Muscle (L5)" layer
    And the error has been resolved by a Sentinel
    When the Kaizen Loop initiates a "Knowledge Extraction"
    Then it must identify the underlying pattern of error
    And it must generate a new "Skill" in YAML format
    And Performance Metric: learning_extraction_time < 10s

  Scenario: Prevent Regression via Shield Injection
    Given a newly crystallized Skill rule
    When an agent attempts to repeat the same error
    Then the L3 Shield must block the action in real-time
    And Performance Metric: veto_propagation < 100ms

Feature: Calibración de Puntuación de Readiness
  Scenario: Downgrade score on degraded Kuzu
    Given a system with Kuzu status DEGRADED
    When the calibrator runs
    Then the memory_spine_readiness score must be less than 10.0

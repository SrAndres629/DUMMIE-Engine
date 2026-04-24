Feature: Agentic Department Segregation [2026]
  Como el Orquestador del Sistema SDD
  Quiero que cada agente respete estrictamente su Locus de responsabilidad
  Para asegurar un flujo de fabricación de software inmutable y verificado

  Scenario: Escalada ante Inconsistencia de Contrato
    Given un agente de "Implementation" detecta que una interfaz es insuficiente para el caso de uso
    When intenta modificar el archivo de contrato en "proto/" o "openapi/"
    Then el sistema debe bloquear la escritura directa
    And forzar al agente a solicitar al "Contract Architect" la evolución formal del esquema

  Scenario: Validación de Comportamiento Mandatoria
    Given el "Clean Coder Pro" ha terminado una funcionalidad
    When el "Formal Validator" audita el código
    Then debe existir un rastro de tests (Suites BDD) generado previamente por el "Behavior Synthesizer"
    And los tests deben ser consistentes con la Spec aprobada

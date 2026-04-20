Feature: Agentic Department Segregation
  Como el Orquestador del Sistema
  Quiero que cada agente respete estrictamente las fronteras de su departamento
  Para asegurar un flujo de valor de software determinista (Fábrica Autárquica)

  Scenario: Escalada Jidoka Obligatoria
    Given un agente de "Engineering" detecta una prueba TDD rota
    When intenta modificar una Especificación en "doc/specs/" para que pase la prueba
    Then el sistema debe bloquear la escritura
    And forzar al agente a usar el protocolo Jidoka y solicitar a "Architecture" la revisión de la Spec

Feature: Cognitive Fabrication and State Management
  Como el Sistema Operativo Agéntico
  Quiero asegurar que la memoria de corto plazo no se evapore
  Para permitir ciclos largos de trabajo (Swarm continuity) sin amnesia

  Scenario: Obligación de State Management Output (SMO)
    Given el agente está trabajando en un refactor masivo
    When el agente decide pausar o devolver el control al PAH
    Then el agente DEBE imprimir el bloque "[SYSTEM_STATE]"
    And detallar "Current Task", "Completed Steps" y "Next Actions"
    And si omite este bloque, la sesión se considera cognitivamente inestable

  Scenario: Bloqueo de escritura sin Spec (SDD Strict)
    Given el Agente 4 (Plant Coder) intenta crear "nueva_logica.py"
    When no existe una especificación correspondiente en "doc/specs/"
    Then el Validador Arquitectónico debe interceptar la llamada
    And rechazar la ejecución con un error "Spec-Driven Development Violation"

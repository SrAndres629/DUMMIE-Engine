Feature: Hybrid Execution and Physical Truth Integrity
  Como el Nodo Sentinel (L2/QA)
  Quiero garantizar que la documentación refleje el estado físico real
  Para prevenir la alucinación de progreso por parte del enjambre

  Scenario: Compilación de Capas Políglotas
    Given el enjambre necesita compilar "L1_Nervous" (Go)
    And el entorno actual no tiene Nix instalado
    When el Agente de Infraestructura intenta compilar
    Then la compilación debe delegarse obligatoriamente a "Docker"
    And cualquier intento de usar comandos locales como "go build" debe ser bloqueado

  Scenario: Prevención de Alucinación Documental
    Given un componente en "layers/l5_muscle/" con estado esquelético
    When el Agente intenta marcar la Spec correspondiente como "FINALIZADA" en el README.md
    Then el Semantic Fabric Indexer debe bloquear la edición
    And emitir una alerta requiriendo que la documentación refleje el estado físico real

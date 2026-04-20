Feature: Agentic Namespace Isolation
  Como el Supervisor L0
  Quiero garantizar que los agentes se comuniquen usando namespaces estrictos
  Para evitar que un agente Plant Coder asuma roles de Arquitectura

  Scenario: Violación de Namespace
    Given el Agente "sw.plant.coder" está activo
    When intenta modificar un archivo en "doc/01_architecture/adr/"
    Then la solicitud de escritura debe ser bloqueada
    And el sistema debe forzar al Agente a solicitar el cambio a "sw.arch.core" vía ACP

  Scenario: Colaboración autorizada vía ACP
    Given el Agente "sw.strategy.discovery" encuentra una dependencia faltante
    When emite un mensaje ACP hacia "sw.plant.infra"
    Then el mensaje debe enrutarse correctamente
    And "sw.plant.infra" debe ejecutar la resolución de dependencia

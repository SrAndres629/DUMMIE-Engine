Feature: Expansión Autónoma de Capacidades
  Como Sistema de Fabricación de Software (SFE)
  Quiero buscar e instalar herramientas MCP o Skills autónomamente
  Para mejorar mi razonamiento, flujo de trabajo y progreso en la programación.

  Scenario: Detección e instalación de una herramienta necesaria
    Given que el sistema detecta una ineficiencia en el análisis de código
    And una herramienta MCP adecuada existe en el registro oficial o comunitario
    When el agente "sw.strategy.discovery" valida la seguridad de la herramienta
    And el agente "sw.arch.core" autoriza su integración
    Then el sistema debe actualizar "mcp_config.json" con la nueva configuración
    And la nueva capacidad debe estar disponible para todo el Swarm

  Scenario: Creación de una Skill personalizada
    Given que no existe una herramienta externa para una necesidad específica
    When el agente "sw.plant.coder" desarrolla una nueva lógica en "L2 Skills"
    Then el sistema debe registrar la nueva habilidad en su Ledger de habilidades
    And el sistema debe ser capaz de reutilizarla en futuros ciclos de fabricación

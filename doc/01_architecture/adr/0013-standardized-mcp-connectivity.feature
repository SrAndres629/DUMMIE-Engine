Feature: Interoperabilidad Universal vía MCP

  Scenario: Un agente se conecta al sistema
    Given un agente de IA compatible con MCP
    When se conecta al puerto de DUMMIE Engine
    Then el servidor MCP debe listar las herramientas de cristalización de memoria
    And debe permitir el acceso a los recursos de especificaciones activas

  Scenario: Registro de una decisión soberana
    Given un agente operando sobre el sistema
    When el agente invoca la herramienta 'crystallize_decision' vía MCP
    Then el sistema debe validar el payload contra el esquema de memoria
    And debe persistir el cambio en '.aiwg/memory/decisions.jsonl'
    And debe devolver un 'causal_hash' válido

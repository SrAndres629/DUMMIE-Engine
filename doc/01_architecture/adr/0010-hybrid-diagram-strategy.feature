Feature: Hybrid Spatial Maintenance
  Como el Nodo de Arquitectura
  Quiero permitir el uso de Mermaid y PlantUML
  Para documentar adecuadamente flujos y estructuras sin estar atado a una sola herramienta

  Scenario: Diagrama de flujo en Mermaid
    Given un archivo de documentación "doc/01_architecture/diagrams/flujo_ejemplo.md"
    When el Agente 2 genera un diagrama interactivo
    Then el bloque de código debe ser de tipo "mermaid"
    And el validador SDD debe aprobar el formato visual

  Scenario: Bloqueo de formato no autorizado
    Given un archivo de documentación
    When el Agente intenta embeber un diagrama en formato "dot" (Graphviz)
    Then el sistema debe fallar la validación porque solo "mermaid" y "plantuml" están autorizados

Feature: Ontological Certainty Calculation
  Como el Nodo Estratega (L0/L2)
  Quiero calcular el nivel de certeza de cada capa del proyecto
  Para evitar escribir código (Plant Coder) en áreas de alta indeterminación teórica

  Scenario: Degradación de certeza tras fallos repetidos
    Given la capa "L4_Edge" tiene una certeza ontológica de 0.8
    And el "Plant Coder" reporta 2 fallos consecutivos en TDD al intentar implementar un adapter HTTP
    When el Audit Loop invoca el cálculo de certeza
    Then el valor de "L4_Edge" en "ontological_map.json" debe descender a 0.5
    And el sistema debe lanzar una tarea de "Discovery" para "L4_Edge" antes de permitir más commits de código

  Scenario: Cristalización completa
    Given la capa "L2_Brain" con Specs completas y TDD en verde
    And todos los ADRs de "L2_Brain" están indexados en el Semantic Fabric
    When el Audit Loop invoca el cálculo de certeza
    Then el valor de "L2_Brain" se establece en 1.0 (Cristalino)

  Performance Metric: mapping_latency < 50ms

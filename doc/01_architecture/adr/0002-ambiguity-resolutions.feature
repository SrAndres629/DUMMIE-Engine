Feature: Ambiguity Resolution Protocol (Jidoka)
  Como el Enjambre Agéntico
  Quiero detener la ejecución ante decisiones no deterministas
  Para evitar escribir código basado en alucinaciones o suposiciones

  Scenario: Detención ante ambigüedad estructural
    Given el Tech Lead está diseñando un esquema de base de datos
    And la Spec no define claramente el tipo de dato para "relevance_score"
    When la entropía de decisión supera el umbral tolerable
    Then el Agente debe activar el protocolo Jidoka (detener la línea)
    And crear un ticket en ".aiwg/memory/ambiguities.jsonl"
    And escalar la decisión al PAH (Humano)

  Scenario: Retoma de operación post-resolución
    Given un ticket resuelto en "resolutions.jsonl"
    When el sistema reinicia el ciclo de diseño
    Then el Agente debe absorber la resolución como verdad absoluta
    And proceder con la implementación sin volver a preguntar

Feature: Metacognitive Identity Evolution
  Como el Nodo de Auditoría Reflexiva (L2)
  Quiero evaluar el historial de resoluciones y ambigüedades
  Para ajustar los traits de identidad y optimizar la autonomía del enjambre

  Scenario: Ajuste de agresividad tras errores de TDD
    Given que el ciclo de sincronización para "L2_Brain" ha concluido
    And el archivo "ambiguities.jsonl" registra más de 3 errores tipo "TDD Failure"
    When el Audit Loop analiza la eficiencia de la sesión
    Then el trait "refactoring_aggressiveness" en "identity.json" debe reducirse en 0.1
    And se debe añadir un registro en "evolution.jsonl" explicando el ajuste por inestabilidad de código
    And el sistema comunica explícitamente al Humano (PAH) la lección aprendida y la mutación de identidad

  Scenario: Incremento de abstracción por éxito repetido
    Given que el enjambre ha resuelto "L3_Shield" sin disparar alarmas Jidoka
    When el Audit Loop analiza la eficiencia de la sesión
    Then el trait "abstraction_level" en "identity.json" debe incrementarse en 0.05
    And el sistema documenta su aumento de confianza en la capa

  Performance Metric: audit_cycle < 100ms

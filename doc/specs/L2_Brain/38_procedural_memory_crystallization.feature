Feature: Cristalización de Memoria Procedimental (DE-V2-L2-38)
  Criterios de Aceptación Ejecutables para el Aprendizaje de Heurísticas.

  Scenario: Extract Logic from Resolved Ambiguity
    Given an "Ambiguity_Ticket" resolved by the PAH
    When the Kaizen Agent analyzes the resolution
    Then it must identify the "Architectural Pattern" used
    And it must generate a new Skill rule in ".agents/skills/"
    And Performance Metric: crystallization_time < 30s

  Scenario: Compact Obsolete Skills (Necro-Learning)
    Given a set of Skills not accessed for 100+ tasks
    When the Memory Engine triggers a "Compresión Multiverso"
    Then the skills must be moved to the L5 "Memoria de Necros"
    And the current prompt context must be reduced
    And Performance Metric: context_reduction > 1000_tokens

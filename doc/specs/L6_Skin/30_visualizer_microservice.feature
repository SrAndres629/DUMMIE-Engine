Feature: Visualizador Topológico 4D (DE-V2-L6-30)
  Criterios de Aceptación Ejecutables para el Visualizador Cinematográfico.

  Scenario: Point-and-Click ADR Lookup
    Given a node in the L6 Canvas
    When the user clicks on the node
    Then the "LST Inspector" must display the associated ADR and Architecture Decision
    And it must show the "Provenance of Inference (PoI)" from Spec 24
    And Performance Metric: lookup_latency < 200ms

  Scenario: Apocalypse (Apoptosis) Activation
    Given a running reasoning saga visible in the Canvas
    When the user activates the "Apoptosis" button
    Then the L0 Arbitrator must terminate the saga immediately
    And the associated SHM buffer must be sanitized
    And Performance Metric: apoptosis_termination_time < 1s

Feature: Design Station Workflow (DE-V2-L2-29)
  Criterios de Aceptación Ejecutables para la Estación de Diseño.

  Scenario: Cognitive Handshake for New Feature
    Given a new feature request "X"
    When the Architect Agent initiates the "Design Handshake"
    Then the system must provide the relevant LST sub-graph
    And it must inject the Personality Constraints (Spec 33)
    And Performance Metric: design_context_injection < 2s

  Scenario: Draft Validation before Physics
    Given a new Spec draft in L0
    When the Sentinel executes the "Semantic Audit"
    Then it must pass the SDD Validator 3.0
    And it must not contradict existing ADRs
    And Performance Metric: draft_validation_time < 5s

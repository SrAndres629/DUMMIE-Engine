Feature: Mental model abstraction layer
  DUMMIE must transform temporal context into governed cognitive state.

  Scenario: Mental model registry exists
    Given the agent loads ".aiwg/mental_models/mental_model_registry.yaml"
    Then it finds the Strategic Partner Model
    And it finds the Engine-Native Integration Model

  Scenario: Context transform is operational
    Given the agent reads ".aiwg/mental_models/context_laplace_transform.md"
    Then it finds input signals
    And it finds transformed states
    And it does not treat the metaphor as real mathematics

  Scenario: State space is parseable
    Given the agent loads ".aiwg/mental_models/context_state_space.json"
    Then objective_state exists
    And phase_state exists
    And session_state exists


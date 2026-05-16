Feature: Plan V1 cognitive evolution operating layer
  DUMMIE must use a canonical roadmap instead of chat memory.

  Scenario: Canonical roadmap exists
    Given the agent loads ".aiwg/evolution/phases.yaml"
    Then it finds 31 registered phases
    And it finds phase "P1"
    And it finds phase "P2"

  Scenario: Current position selects next phase
    Given the agent loads ".aiwg/evolution/current_position.json"
    And the agent loads ".aiwg/evolution/next_phase_seed.json"
    Then current phase is "P1"
    And next required phase is "P2"

  Scenario: Roadmap drift is forbidden
    Given the agent has chat memory
    When canonical roadmap files are available
    Then the agent must not redefine the roadmap from chat memory


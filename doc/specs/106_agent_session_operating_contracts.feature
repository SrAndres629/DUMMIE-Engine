Feature: Agent session operating contracts
  All local agent environments must obey the canonical roadmap.

  Scenario: Universal session contract loads roadmap state
    Given the agent reads ".aiwg/session_contracts/UNIVERSAL_AGENT_SESSION_CONTRACT.md"
    Then it must load ".aiwg/evolution/current_position.json"
    And it must load ".aiwg/evolution/next_phase_seed.json"

  Scenario: Codex does not claim PASS without evidence
    Given Codex CLI performs scoped edits
    When tests are absent or failing
    Then Codex must document the absence or failure

  Scenario: IDE sessions avoid roadmap drift
    Given an Antigravity IDE session starts from chat context
    When ".aiwg/evolution/" is available
    Then the session must not redefine the roadmap from chat memory


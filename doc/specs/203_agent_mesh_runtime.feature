Feature: Agent Mesh Runtime
  As DUMMIE Engine
  I want every supported agentic CLI to receive a native boot bundle and mailbox channels
  So that multiple probabilistic engines can coordinate through one orchestrated runtime.

  Scenario: Bootstrap built-in CLI agents
    Given the agent mesh runtime is empty
    When the mesh bootstrap runs
    Then profiles exist for codex_cli, gemini_cli, antigravity, and opencode
    And every profile has inbox and control inputs
    And every profile has outbox and handoff outputs

  Scenario: Route a message between CLIs
    Given codex_cli and gemini_cli are registered agents
    When codex_cli sends a handoff message to gemini_cli
    Then the message is written to gemini_cli inbox
    And the same message is written to codex_cli outbox

  Scenario: Dynamic lifecycle remains gated
    Given the mesh status is requested
    When process supervision is not yet verified
    Then future_spawn_close_enabled is false
    And model_specific_boot_profiles is true

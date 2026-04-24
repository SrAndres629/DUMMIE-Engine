Feature: ADR-0017 - Environment Decoupling and Agent Config Fix

  Scenario: Overseer-meta Agent tool names are valid
    Given the agent configuration file ".gemini/agents/overseer-meta.md"
    Then it should contain "mcp_sequentialthinking_sequentialthinking"
    And it should contain "run_shell_command"

  Scenario: L1 Nervous environment is isolated
    Given the directory "layers/l1_nervous/.venv"
    Then it should be a valid python virtual environment
    And it should be used in "dummie_agent_config.json" for L1 related tasks

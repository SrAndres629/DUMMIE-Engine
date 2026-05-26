Feature: OpenCode Native Integration
  DUMMIE Engine como kernel cognitivo, OpenCode como shell de interfaz

  Scenario: Config generation from SSOT
    Given DUMMIE SSOTs exist at configs/models_config.json and dummie_gateway_config.json
    When generate_opencode_config.py runs
    Then it produces valid opencode.jsonc with dummie-brain MCP server
    And it includes dummie-opencode plugin reference
    And the generated config matches the MCP servers from dummie_gateway_config.json

  Scenario: Plugin hooks MetaGateway routing
    Given the dummie-opencode plugin is loaded in opencode
    When a user sends a message "genera una imagen de un paisaje"
    Then the chat.params hook fires
    And the message is routed through MetaGateway
    And the domain is media_generation
    And the sub-gateway assigned is media

  Scenario: Tool execution with SDD guardrails
    Given the dummie-opencode plugin is loaded in opencode
    When a tool.execute.before hook fires for a remote capability
    Then SDD guardrails are checked before execution
    And the tool is only executed if SDD permits

  Scenario: Multi-session domain isolation
    Given two opencode sessions exist
    When session A sends "genera un video" and session B sends "git status"
    Then session A routes to media gateway
    And session B routes to code gateway
    And sessions have independent context

  Scenario: Qwen3-Embedding as routing model
    Given Qwen3-Embedding is installed in Ollama
    When the EmbeddingMatchStrategy receives a query
    Then it uses Qwen3-Embedding for embedding generation
    And the dimensions are correctly configured (not 384)
    And the similarity threshold is 0.35

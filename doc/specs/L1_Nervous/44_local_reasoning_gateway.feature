Feature: Local Reasoning Gateway contract
  As the DUMMIE Engine runtime
  I want local reasoning to improve recall and tool selection through MCP
  So that cloud agents receive grounded, compact, measurable context

  Scenario: public access stays behind the Meta-Gateway
    Given the local reasoning tools are registered
    Then they are discoverable through dummie-brain master tools
    And Performance Metric: latency < 100ms

  Scenario: Gemma is a reranker and context shaper
    Given embeddings returned candidate tools and artifacts
    Then local reasoning ranks and shapes context without executing side effects
    And Performance Metric: latency < 100ms

  Scenario: degraded mode is explicit
    Given no local model runtime is available
    Then deterministic fallback still returns auditable recommendations
    And Performance Metric: latency < 100ms
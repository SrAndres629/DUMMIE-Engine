Feature: Socraticode Gateway Adapter
  Scenario: Perform semantic search with MCP
    Given an available MCP gateway
    When I perform a semantic search
    Then the adapter queries the MCP
    And Performance Metric: latency < 100ms
    And returns a READY status with normalized results

  Scenario: Fallback to VaultEmbeddingIndex
    Given an unavailable MCP gateway
    When I perform a semantic search
    Then the adapter falls back to the local index
    And Performance Metric: latency < 100ms
    And returns a DEGRADED status with normalized results
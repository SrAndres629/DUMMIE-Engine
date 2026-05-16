Feature: Entrypoint de Memoria Causal
  Scenario: fallback to file-backed memory
    Given Kuzu is unavailable
    When the memory spine entrypoint is queried
    Then the status must be DEGRADED_WITH_FILE_BACKED_MEMORY

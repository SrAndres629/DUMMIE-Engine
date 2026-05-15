Feature: Knowledge Vault
  Scenario: Promoting a successful mission to the Vault
    Given a finalized workbench for mission "m123" with status "SUCCESS"
    When the VaultCurator extracts candidates
    Then a "golden_path" entry should be created in ".aiwg/vault/"
    And Performance Metric: latency < 100ms
    And it must reference mission "m123"

  Scenario: Preventing promotion of secrets
    Given a workbench artifact containing the string "API_KEY"
    When the VaultCurator processes the artifact
    Then the operation must block or strip the sensitive data
    And Performance Metric: latency < 100ms
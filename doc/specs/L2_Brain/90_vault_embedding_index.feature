Feature: Vault Embedding Index
  Scenario: Index a Vault Entry
    Given a VaultEntry from a mission
    When I index the entry in the embedding index
    Then a deterministic fake vector is generated
    And Performance Metric: latency < 100ms
    And the entry is saved in vault_embedding_index.json
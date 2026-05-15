Feature: Vault Embedding Index
  Scenario: Index a Vault Entry
    Given a VaultEntry from a mission
    When I index the entry in the embedding index
    Then a deterministic fake vector is generated
    And the entry is saved in vault_embedding_index.json

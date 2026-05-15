Feature: Knowledge Vault Curator

  Scenario: Extract and store a golden path entry
    Given a finalized workbench for mission "m1"
    When I curate the workbench "m1"
    Then a new vault entry of type "golden_path" should be created
    And Performance Metric: latency < 100ms
    And the vault index should be updated
    And no private reasoning should be stored in the vault
Feature: Graph Synchronization Planning
  Scenario: Generate a GraphSyncPlan from MemoryRefs
    Given a list of MemoryRefs (LearningEpisodes and VaultEntries)
    When I generate a GraphSyncPlan
    Then the plan contains deterministic nodes for each ref
    And the plan identifies relationships (edges) between them
    And the plan defaults to dry_run mode

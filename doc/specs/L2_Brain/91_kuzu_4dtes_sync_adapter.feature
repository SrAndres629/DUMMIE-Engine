Feature: Kuzu Graph Sync Adapter
  Scenario: Validate a GraphSyncPlan
    Given a valid GraphSyncPlan
    When I validate it via the Kuzu adapter
    Then the adapter confirms it is safe to apply
    And Performance Metric: latency < 100ms
  
  Scenario: Apply plan with writes disabled
    Given a valid GraphSyncPlan
    When I attempt to apply it with allow_write=False
    Then the adapter performs a dry-run and skips actual writes
    And Performance Metric: latency < 100ms
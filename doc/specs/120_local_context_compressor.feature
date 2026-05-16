Feature: Local context compression
  Scenario: Required items are preserved
    Given required and optional context items
    When compressor runs
    Then required items are not dropped

  Scenario: Stale optional items are compressed or dropped
    Given stale optional context items
    When compressor runs
    Then stale optional items are not preserved by default

  Scenario: Secret/private reasoning is rejected
    Given secret-like or private reasoning content
    When compressor validates items
    Then it raises an error
